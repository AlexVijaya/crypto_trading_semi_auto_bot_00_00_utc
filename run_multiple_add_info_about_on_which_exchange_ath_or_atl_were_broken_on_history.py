import subprocess
import sys
import time
import os
import shutil
import datetime
import pprint
import sys
import subprocess

def run_upload_file_script(python_file_name_to_run):
    interpreter = sys.executable
    subprocess.run([interpreter, python_file_name_to_run])


def delete_files_in_current_rebound_breakout_and_false_breakout():
  # Get current directory
  current_dir = os.getcwd()

  # Construct path to subfolder
  subfolder_path = os.path.join(current_dir, 'current_rebound_breakout_and_false_breakout')

  file_path_to_delete=\
      get_file_name_for_deletion(subdirectory_name='current_rebound_breakout_and_false_breakout')


  # Check if subfolder exists
  if not os.path.exists(subfolder_path):
    print("subfolder doesn't exist")
    return

  # Delete all files in subfolder
  for filename in os.listdir(subfolder_path):

    file_path = os.path.join(subfolder_path, filename)
    if file_path!=file_path_to_delete:
        continue
    try:
      if os.path.isfile(file_path) or os.path.islink(file_path):
        os.unlink(file_path)
      elif os.path.isdir(file_path):
        shutil.rmtree(file_path)
    except Exception as e:
      print('Failed to delete %s. Reason: %s' % (file_path, e))

def get_file_name_for_deletion(subdirectory_name='current_rebound_breakout_and_false_breakout'):

    # Declare the path to the current directory
    current_directory = os.getcwd()

    # Create the subdirectory in the current directory if it does not exist
    subdirectory_path = os.path.join(current_directory, subdirectory_name)
    os.makedirs(subdirectory_path, exist_ok=True)

    # Get the current date
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    # Create the file path by combining the subdirectory and the file name (today's date)
    file_path = os.path.join(subdirectory_path, "crypto_" + today + '.txt')
    return file_path

# database_name="ohlcv_1d_data_for_usdt_pairs_0000_for_todays_pairs"
# engine_for_db_with_todays_ohlcv1, connection_to_ohlcv_for_usdt_pairs1 = \
#     connect_to_postgres_db_without_deleting_it_first(database_name)

def run_multiple_search_current_rebound_breakout_false_breakout_situations():
    # Run the Python script and capture its output

    delete_files_in_current_rebound_breakout_and_false_breakout()

    # Get the path to the Python interpreter executable
    interpreter = sys.executable




    print(interpreter)
    files = ['add_exchanges_where_pair_was_traded_at_time_of_bfr_to_column_in_bfr_tables_B1ATH.py',
             'add_exchanges_where_pair_was_traded_at_time_of_bfr_to_column_in_bfr_tables_B2ATH.py',
             'add_exchanges_where_pair_was_traded_at_time_of_bfr_to_column_in_bfr_tables_B1ATL_beginning.py',
             'add_exchanges_where_pair_was_traded_at_time_of_bfr_to_column_in_bfr_tables_B1ATL_middle.py',
             'add_exchanges_where_pair_was_traded_at_time_of_bfr_to_column_in_bfr_tables_B1ATL_end.py',
             'add_exchanges_where_pair_was_traded_at_time_of_bfr_to_column_in_bfr_tables_B2ATL.py',
             'add_exchanges_where_pair_was_traded_at_time_of_bfr_to_column_in_bfr_tables_FB1ATH.py',
             'add_exchanges_where_pair_was_traded_at_time_of_bfr_to_column_in_bfr_tables_FB1ATL.py',
             'add_exchanges_where_pair_was_traded_at_time_of_bfr_to_column_in_bfr_tables_FB2ATH.py',
             'add_exchanges_where_pair_was_traded_at_time_of_bfr_to_column_in_bfr_tables_FB1ATL.py',
             'add_exchanges_where_pair_was_traded_at_time_of_bfr_to_column_in_bfr_tables_RATH.py',
             'add_exchanges_where_pair_was_traded_at_time_of_bfr_to_column_in_bfr_tables_RATL.py',

             ]

    # Run each Python file in the list in parallel
    processes = []
    for file in files:
        process = subprocess.Popen([f'{interpreter}', file])
        processes.append(process)

    # Wait for the processes to complete and get their output
    # outputs = []
    for process in processes:
        output, _ = process.communicate()
        # outputs.append(output.decode())

    # # Print the output of the processes
    # for output in outputs:
    #     print(output)
    #     # pprint.print(output)
if __name__=="__main__":
    start_time = time.time()

    run_multiple_search_current_rebound_breakout_false_breakout_situations()

    python_file_name_to_run = "upload_file_to_goggle_drive2.py"
    run_upload_file_script(python_file_name_to_run)



    end_time = time.time()
    overall_time = end_time - start_time
    print('overall time in minutes=', overall_time / 60.0)
    print('overall time in hours=', overall_time / 60.0 / 60.0)