# 栅格分级赋色处理用于展示
import os
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling


def reclass_coloring(src_path, dst_path, reform_dic):
    with rasterio.open(src_path) as src:
        src_arr = src.read(1)
        meta = src.meta
    threshold = reform_dic['threshold']
    dst_value = reform_dic['dst_value']
    color_map = reform_dic['color_map']
    # reclass
    if len(threshold) != len(dst_value):
        print('the input out_value do not match threshold!')
        return
    dst_arr = src_arr.copy()
    for i in range(len(threshold)):
        if i != (len(threshold) - 1):
            dst_arr[(src_arr > threshold[i]) & (src_arr <= threshold[i + 1])] = dst_value[i]
        else:
            dst_arr[src_arr > threshold[i]] = dst_value[i]
    # coloring
    dst_arr[np.isnan(dst_arr)] = 0
    meta.update({'nodata': 0})
    meta.update({'dtype': 'uint8'})
    with rasterio.open(dst_path, 'w', **meta) as dst:
        dst_arr = dst_arr.astype('uint8')
        dst.write(dst_arr, indexes=1)
        dst.write_colormap(1, color_map)


def reproject2wgs84(src_path, dst_path):
    dataset = rasterio.open(src_path)
    dataread = dataset.read()
    dataread = dataread.astype('uint8')
    dst_crs = 'EPSG:4326'
    transform, width, height = calculate_default_transform(
        dataset.crs, dst_crs, dataset.width, dataset.height, *dataset.bounds)
    kwargs = dataset.profile.copy()
    kwargs.update({
        'crs': dst_crs,
        'transform': transform,
        'width': width,
        'height': height,
        'dtype': rasterio.uint8,
    })
    with rasterio.open(dst_path, 'w', **kwargs) as dst:
        for i in range(1, dataset.count + 1):
            reproject(
                source=dataread[i - 1],
                destination=rasterio.band(dst, i),
                src_transform=dataset.transform,
                src_crs=dataset.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest)


if __name__ == '__main__':
    # src_file = 'G:/VScodeProjects/air_pollution_surveillance/raster_process_for_display/air_pollution_pm2p5.tif'
    # reprojected_file = src_file.split('.')[0] + '_reprojected.tif'
    # dst_file = reprojected_file.split('.')[0] + '_color.tif'
    # reform_dic = {'threshold': [0, 35, 75, 115, 150, 250],
    #               'dst_value': [1, 2, 3, 4, 5, 6],
    #               'color_map': {
    #                   1: (8, 8, 255),
    #                   2: (59, 157, 255),
    #                   3: (112, 255, 210),
    #                   4: (231, 255, 74),
    #                   5: (255, 166, 0),
    #                   6: (255, 0, 0)}}
    # reproject2wgs84(src_file, reprojected_file)
    # reclass_coloring(reprojected_file, dst_file, reform_dic)

    # 以下代码为下载的H8pm2.5tif数据分级赋色
    # input_dir = 'F:/zsk/H8/demo/output/l4/China'
    # output_dir = 'F:/zsk/H8/demo/output/l4/China_color/color_2'

    # for d in os.listdir(input_dir):
    #     d_dir = os.path.join(input_dir, d)
    #     out_d_dir = os.path.join(output_dir, d)
    #     if not os.path.exists(out_d_dir):
    #         os.mkdir(out_d_dir)
    #     for src_file in os.listdir(d_dir):
    #         reprojected_name = src_file.split('.')[0] + '_reprojected.tif'
    #         dst_name = reprojected_name.split('.')[0] + '_color.tif'
    #         reprojected_file = os.path.join(out_d_dir, reprojected_name)
    #         dst_file = os.path.join(out_d_dir, dst_name)
    #         reform_dic = {'threshold': [0, 35, 75, 115, 150, 250],
    #                       'dst_value': [1, 2, 3, 4, 5, 6],
    #                       'color_map': {
    #                                     1: (0, 97, 0),
    #                                     2: (97, 153, 0),
    #                                     3: (197, 219, 0),
    #                                     4: (255, 217, 0),
    #                                     5: (255, 132, 0),
    #                                     6: (255, 38, 0)}}
    #         src_file_path = os.path.join(d_dir, src_file)
    #         # reproject2wgs84(src_file_path, reprojected_file)
    #         reclass_coloring(src_file_path, dst_file, reform_dic)

    db_tif_dir = 'F:/zsk/H8/demo/db/black_tif'
    output_dir = 'F:/zsk/H8/demo/db/color_tif/color_2'

    for day in os.listdir(db_tif_dir):
        day_dir = os.path.join(db_tif_dir, day)
        out_day_dir = os.path.join(output_dir, day)
        if not os.path.exists(out_day_dir):
            os.mkdir(out_day_dir)
        for f in os.listdir(day_dir):
            if f.endswith('.tif'):
                reprojected_file_name = f.split('.')[0] + '_reprojected.tif'
                dst_file_name = reprojected_file_name.split('.')[0] + '_color.tif'
                reform_dic = {'threshold': [0, 35, 75, 115, 150, 250],
                              'dst_value': [1, 2, 3, 4, 5, 6],
                              'color_map': {
                                            # 1: (40, 146, 199),
                                            # 2: (140, 184, 164),
                                            # 3: (215, 227, 125),
                                            # 4: (252, 207, 81),
                                            # 5: (247, 122, 45),
                                            # 6: (232, 21, 21)}}
                                            # 1: (0, 97, 0),
                                            1: (0, 97, 0),
                                            2: (97, 153, 0),
                                            3: (197, 219, 0),
                                            4: (255, 217, 0),
                                            5: (255, 132, 0),
                                            6: (255, 38, 0)}}
                src_file = os.path.join(day_dir, f)
                reprojected_file = os.path.join(out_day_dir, reprojected_file_name)
                dst_file = os.path.join(out_day_dir, dst_file_name)
                reproject2wgs84(src_file, reprojected_file)
                reclass_coloring(reprojected_file, dst_file, reform_dic)
                os.remove(reprojected_file)

