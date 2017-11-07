import sys
import os
from common import PostProcess, update_metrics_in_report_json
from common import read_limits, check_limits_and_add_to_report_json


if __name__ == '__main__':
    try:
        mat_file_name = sys.argv[1]
        if not os.path.exists(mat_file_name):
            print 'Given result file does not exist: {0}'.format(sys.argv[1])
            os._exit(3)

        ## First limit part
        limit_dict, filter = read_limits()
        ## End of first limit part
        
        ## Post processing part
        filter.append('road_Wheel_Load_Both_Sides.vehicleSpeed')

        # loads results with the filtered out variables (and 'time' which is default)
        pp = PostProcess(mat_file_name, filter)
        #pressure_variable_name = [var_name for var_name in filter if var_name.endswith('hot_fluid_out.p')][0]
        metrics = {}
        metrics.update({'VehicleSpeed': {'value': pp.global_max("road_Wheel_Load_Both_Sides.vehicleSpeed"), 'unit': 'kph'}})
        #metrics.update({'EngineAirPressure': {'value': pp.last_value(pressure_variable_name), 'unit': 'Pascal'}})

        cwd = os.getcwd()
        os.chdir('..')
        update_metrics_in_report_json(metrics)
        ## end of postprocessing part

        ## Second limit part
        check_limits_and_add_to_report_json(pp, limit_dict)
        ## end of Second limit part
        os.chdir(cwd)
    except Exception as err:
        print err.message
        if os.name == 'nt':
            import win32api
            win32api.TerminateProcess(win32api.GetCurrentProcess(), 1)
        else:
            sys.exit(1)

