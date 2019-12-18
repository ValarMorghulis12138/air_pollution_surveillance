# python直接从db文件中读取数据库中的空气质量信息并生成excel、shp、raster
import sqlite3
import sys
import os
from osgeo import gdal
import osgeo.ogr as ogr
import osgeo.osr as osr
sys.path.append("./")
from lonlat_search_gaodeapi import gaode_search


def data_reader(db_path, data_time):
    # db_path = "C:/Users/codhy/Desktop/空气质量/environmental_new.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sql = """SELECT * FROM "main"."environmental_quality" WHERE "time" LIKE '%""" + data_time + """%'"""
    print(sql)
    cursor.execute(sql)
    result = cursor.fetchall()
    # print(type(result))
    # print(len(result))
    # print(result[0])
    # print(type(result[0]))
    conn.close()
    # sql返回的result为每个元素为turple的list，其中每个turple为数据库中的每条记录，turple
    # 的每个元素类型为str
    return result


def list2shp(data_list, shp_path):
    # 若有该时刻的数据则查询高德api获取点位经纬度信息并将记录写入shapefile中
    # 调用gdal新建shapefile
    gdal.AllRegister()
    # 为了支持中文路径，请添加下面这句代码
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # 为了使属性表字段支持中文，请添加下面这句
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
    # 注册所有的驱动
    ogr.RegisterAll()
    # set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")
    # create the data source
    data_source = driver.CreateDataSource(shp_path)
    # create the spatial reference, WGS84
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    # create the layer
    layer = data_source.CreateLayer("surveillance_stations", srs, ogr.wkbPoint)
    # Add the fields we're interested in
    field_city = ogr.FieldDefn("City", ogr.OFTString)
    field_city.SetWidth(24)
    layer.CreateField(field_city)
    field_time = ogr.FieldDefn("Time", ogr.OFTString)
    field_time.SetWidth(24)
    layer.CreateField(field_time)
    layer.CreateField(ogr.FieldDefn("Latitude", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Longitude", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("AQI", ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("Pm2.5", ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("Pm10", ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("SO2", ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("NO2", ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("CO", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("O3", ogr.OFTInteger))

    for i in range(len(data_list)):
        # data_list每个元素为turple，先转为list
        row_data = list(data_list[i])
        # 根据每个城市名搜索该城市的经纬度坐标，返回的lon lat类型为str
        lon, lat = gaode_search.getGeoForAddress(row_data[0])

        if (lon is not None) and (lat is not None):
            # create the feature
            feature = ogr.Feature(layer.GetLayerDefn())
            # Set the attributes using the values from the delimited text file
            feature.SetField("City", row_data[0])
            feature.SetField("Time", row_data[9])
            feature.SetField("Longitude", float(lon))
            feature.SetField("Latitude", float(lat))
            feature.SetField("AQI", int(row_data[1].replace('—', '-1')))
            feature.SetField("Pm2.5", int(row_data[2].replace('—', '-1')))
            feature.SetField("Pm10", int(row_data[3].replace('—', '-1')))
            feature.SetField("SO2", int(row_data[4].replace('—', '-1')))
            feature.SetField("NO2", int(row_data[5].replace('—', '-1')))
            feature.SetField("CO", float(row_data[6].replace('—', '-1')))
            feature.SetField("O3", int(row_data[7].replace('—', '-1')))
            # create the WKT for the feature using Python string formatting
            wkt = "POINT(%f %f)" % (float(lon), float(lat))
            # Create the point from the Well Known Txt
            point = ogr.CreateGeometryFromWkt(wkt)
            # Set the feature geometry using the point
            feature.SetGeometry(point)
            # Create the feature in the layer (shapefile)
            layer.CreateFeature(feature)
            # Dereference the feature
            feature = None
    # Save and close the data source
    data_source = None


if __name__ == "__main__":
    db_path = "C:/Users/codhy/Desktop/空气质量/environmental_new.db"
    output_dir = "F:/zsk/H8/demo/db"    
    china_shp = "G:/VScodeProjects/air_pollution_surveillance/geoed_excel_to_raster/china_extent.shp"
    year = 2019
    month = 12
    for day in range(1, 13):
        for clock in range(24):
            if day < 10:
                day_str = '0' + str(day)
            else:
                day_str = str(day)
            if clock < 10:
                clock_str = '0' + str(clock)
            else:
                clock_str = str(clock)
            data_time_str = "%s年%s月%s日%s时" % (year, month, day_str, clock_str)
            data_list = data_reader(db_path, data_time_str)
            if len(data_list) > 0:
                result_time = str(year) + str(month) + day_str + clock_str
                result_dir = os.path.join(output_dir, result_time)
                if not os.path.exists(result_dir):
                    os.mkdir(result_dir)
                result_shp_path = os.path.join(result_dir, result_time + '.shp')
                result_ras_path = os.path.join(result_dir, result_time + '.tif')
                list2shp(data_list, result_shp_path)
                # convert shapefile to raster using gdal
                raw_raster = os.path.join(result_dir, 'raw_ratser.tif')
                gdal.Grid(raw_raster, result_shp_path, format='GTiff', zfield='Pm2.5',
                          outputBounds=[73.4, 54, 135.1, 18.1],
                          algorithm='invdist:power=2.0:smoothing=0.1')
                # clip to china extent using gdal
                gdal.Warp(result_ras_path, raw_raster, format="GTiff",
                          warpOptions="NUM_THREADS=ALL_CPUS", warpMemoryLimit=1024,
                          resampleAlg="cubic", multithread=True,
                          cutlineDSName=china_shp, cropToCutline=True)
                os.remove(raw_raster)