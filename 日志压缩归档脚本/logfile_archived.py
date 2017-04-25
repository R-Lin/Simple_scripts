# coding:utf8
import glob
import os
import sys
import yaml
import zipfile
from collections import defaultdict
from time import strftime, localtime, time, clock

from comm import comm_logging


def mkdir_dir(dir_name):
    # mkdir log_arch
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

if __name__ == '__main__':

    now_time_suffix, now_timestamp = strftime('%Y%m', localtime()), time()
    start_runtime = clock()
    # script_path and logger config
    sript_dir, script_name = os.path.split(sys.argv[0])
    if sript_dir:
        os.chdir(sript_dir)
    log_name = script_name.replace('.', '_') + '.log'
    log = comm_logging.log_init(log_name, script_dir=sript_dir)

    try:
        log_conf_dict = yaml.load(open('conf/logfile_arch.yaml'))
    except yaml.parser.ParserError as error_messag:
        log.error(str(error_messag).replace('\n', ''))
        sys.exit()

    logfile_keep_time_defalut = log_conf_dict['keep_time']
    logfile_arch_time = log_conf_dict['arch_time']
    logfile_save_path = log_conf_dict['dst_dir']
    logfile_item_list = log_conf_dict['project_list']
    result_date_dic = {}
    project_name_dic = {}

    # Build log tree dict
    for logfile_item in logfile_item_list:
        logfile_list = logfile_item['paths']
        project_name_dic[logfile_item['name']] = {}
        for logfile in logfile_list:
            logfile_keep_time = logfile.get('keep_time', logfile_keep_time_defalut)
            log_path = logfile['log_path']


            log_file_dir = os.path.basename(os.path.dirname(log_path))
            log_files = glob.glob(log_path)

            if not log_files:
                # no logfles
                continue

            for log_file_item in iter(log_files):
                is_del = 0
                file_ctimestamp = os.stat(log_file_item).st_mtime
                time_suffix = strftime('%Y%m', localtime(file_ctimestamp))
                reduce_value = now_timestamp - file_ctimestamp
                if reduce_value <= logfile_arch_time:
                    # keep one month logs
                    continue
                if reduce_value >= logfile_arch_time:
                    # delete flag
                    is_del = 1
                try:
                    file_suffix = os.path.basename(log_file_item).split('.')[-1]
                except IndexError:
                    log.error('logfile_path must have filename suffix! e.g: *.log, info.log..')
                    sys.exit()
                dirname_file_suffix = (os.path.basename(os.path.dirname(log_file_item)), file_suffix)

                # dirname and file suffix make up the defalutdict_key: api::log
                defaultdict_key = '::'.join(dirname_file_suffix)
                if defaultdict_key not in project_name_dic[logfile_item['name']]:
                    # avoid the path is *, accoding the file to bulit defaultdict
                    project_name_dic[logfile_item['name']][defaultdict_key] = defaultdict(list)
                project_name_dic[logfile_item['name']][defaultdict_key][time_suffix].append((is_del, log_file_item))

    # Arch log
    for project_name in project_name_dic:
        for dirname_file_suffix in project_name_dic[project_name]:
            log_path_dir, file_suffix = dirname_file_suffix.split('::')
            for log_timesuffix_dir in project_name_dic[project_name][dirname_file_suffix]:
                dest_path = os.path.join(logfile_save_path, project_name, log_path_dir)
                mkdir_dir(dest_path)
                arch_logfile_name = '%s_%s-%s.zip' % (log_path_dir, file_suffix, log_timesuffix_dir)
                arch_logfile_target = os.path.join(dest_path, arch_logfile_name)
                already_arch_file_list = []
                if os.path.exists(arch_logfile_target):
                    with zipfile.ZipFile(arch_logfile_target) as f_r:
                        already_arch_file_list = f_r.namelist()
                with zipfile.ZipFile(arch_logfile_target, 'a', zipfile.ZIP_DEFLATED, allowZip64=True) as f:
                    delete_list = []
                    for del_flag, log_file in project_name_dic[project_name][dirname_file_suffix][log_timesuffix_dir]:
                        basename = os.path.basename(log_file)
                        if basename not in already_arch_file_list:
                            f.write(log_file, os.path.basename(log_file))
                            log.info('%s has completed!' % log_file)
                        if del_flag:
                            # add to delete_list
                            delete_list.append(log_file)

                log.info('%s all completed!' % arch_logfile_target)
                # delete file that had arched
                for delete_file in delete_list:
                    os.remove(delete_file)
                    log.info('%s had deleted!' % delete_file)
    spent_time = clock() - start_runtime
    log.info('script spent time: %s s' % spent_time)
