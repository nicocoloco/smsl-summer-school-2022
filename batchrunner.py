from covid_model.model import *
import json
import pickle
import copy

def batchrun(iterations, steps, simulation_id, variable_params, fixed_params, contact_matrix, output_dir):
    print("running...")
    for i in range(iterations):
        # print("Iteration: %i/%i" % ((i+1), iterations))

        model = Covid19Model(copy.deepcopy(variable_params), fixed_params, contact_matrix)

        for j in range(steps):
            model.step()

        output = {
            "seirdv_total_time_series": model.data_collector_total.get_model_vars_dataframe(),
            "seirdv_age_time_series": model.data_collector_age.get_model_vars_dataframe(),
            "seirdv_total_final": model.total
        }

        output_filename = "%s/%s_iter_%i.pkl" % (output_dir, simulation_id, i)
        with open(output_filename, "wb") as output_file:
            pickle.dump(output, output_file, -1) # -1 specifies highest binary protocol

        del output
        del model

    print("Batch run finished.")