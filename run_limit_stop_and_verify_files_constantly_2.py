import sys
from subprocess import Popen, PIPE
import streamlit as st
import subprocess
import os
import psutil
import signal
def get_pids_by_full_command(process_name):
    process_name = process_name.replace('"', '\\"')  # Escape double quotes if present
    command = f"pgrep -f '{process_name}'"
    print("command")
    print(command)
    pids = []

    try:
        output = subprocess.check_output(command, shell=True, text=True)
        print("output")
        print(output)
        # Split the output by lines to get multiple PIDs
        pids = output.strip().split('\n')
    except subprocess.CalledProcessError:
        pass  # Handle errors when no process matches the command

    return pids

def get_pid_by_name(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            return proc.info['pid']
    return None  # Return None if the process with the specified name is not found

def kill_process_by_pid(pid):
    try:
        os.kill(pid, signal.SIGTERM)  # Send a termination signal to the process
        print(f"Process with PID {pid} killed successfully.")
    except OSError:
        print(f"Failed to kill process with PID {pid}.")
if __name__=="__main__":

    pids=[]
    if st.button(f"run place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file_no_use_of_popen"):
        command_args1 = [sys.executable,'place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file_no_use_of_popen.py']
        process1 = Popen(command_args1 )

    if st.button("run place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file_without_running_verify_no_use_of_popen"):
        command_args2 = [sys.executable,'place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file_without_running_verify_no_use_of_popen']
        process2 = Popen(command_args2)

    if st.button("run verify_that_all_pairs_from_df_are_ready_for_bfr_google_spreadsheed_is_used_popen_is_not_used"):
        command_args3 = [sys.executable,'verify_that_all_pairs_from_df_are_ready_for_bfr_google_spreadsheed_is_used_popen_is_not_used']
        process3 = Popen(command_args3)


    # process_names = ["place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file_no_use_of_popen.py",
    #                  "place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file_without_running_verify_no_use_of_popen",
    #                  "verify_that_all_pairs_from_df_are_ready_for_bfr_google_spreadsheed_is_used_popen_is_not_used"]
    # for process_name in process_names:
    #
    #     pids = get_pids_by_full_command(process_name)
    #     print("pids")
    #     print(pids)
    #     if pids:
    #         st.write(f"PIDs of process '{process_name}': {', '.join(pids)}")
    #         for pid in pids:
    #             if st.button(f"kill the process with {pid}"):
    #                 result = kill_process_by_pid(int(pid))
    #                 st.write(result)
    #     else:
    #         st.write(f"No process matching '{process_name}' found.")
