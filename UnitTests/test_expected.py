import os
import argparse

report = '''
[
 {
  "baseline_color_path": "../../../Baseline/Cameras/Color/Camera_Cube_Map.jpg",
  "baseline_opacity_path": "../../../Baseline/Cameras/Opacity/Camera_Cube_Map.jpg",
  "date_time": "2018-02-16_12-15-12",
  "difference_color": 0.0,
  "difference_opacity": 0.0,
  "file_name": "Camera_Cube_Map.jpg",
  "render_color_path": "Color/Camera_Cube_Map.jpg",
  "render_device": "AMD Radeon R9 200  HD 7900 Series ",
  "render_opacity_path": "Opacity/Camera_Cube_Map.jpg",
  "render_time": 26.91,
  "render_version": "2.2.128",
  "scene_name": "Camera_Cube_Map.mb",
  "test_name": "Cameras",
  "tool": "maya2017"
 },
 {
  "baseline_color_path": "../../../Baseline/Cameras/Color/Camera_Cube_Map_Stereo.jpg",
  "baseline_opacity_path": "../../../Baseline/Cameras/Opacity/Camera_Cube_Map_Stereo.jpg",
  "date_time": "2018-02-16_12-15-37",
  "difference_color": 0.0,
  "difference_opacity": 0.0,
  "file_name": "Camera_Cube_Map_Stereo.jpg",
  "render_color_path": "Color/Camera_Cube_Map_Stereo.jpg",
  "render_device": "AMD Radeon R9 200  HD 7900 Series ",
  "render_opacity_path": "Opacity/Camera_Cube_Map_Stereo.jpg",
  "render_time": 25.37,
  "render_version": "2.2.128",
  "scene_name": "Camera_Cube_Map_Stereo.mb",
  "test_name": "Cameras",
  "tool": "maya2017"
 }
]
'''

expected = '''
[
  {"file_path": "Color/Camera_Cube_Map.jpg"},
  {"file_path": "Color/Camera_Cube_Map_Stereo.jpg"},
  {"file_path": "Color/1_Cube_Map_Stereo.jpg"}
]
'''

def createArgParser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--work_dir')

    return argparser

if __name__ == '__main__':
    args = createArgParser().parse_args()

    try:
        os.makedirs(os.path.abspath(args.work_dir))
    except:
        pass

    with open(os.path.join(args.work_dir, 'report.json'), 'w') as file:
        file.write(report)

    with open(os.path.join(args.work_dir, 'expected.json'), 'w') as file:
        file.write(expected)
