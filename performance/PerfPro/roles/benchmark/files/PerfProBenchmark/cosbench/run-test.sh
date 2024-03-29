#!/bin/sh
#
# Seagate-tools: PerfPro
#
# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#
# -*- coding: utf-8 -*-

set -e
SHORT=h
LONG=help,interactive,controller:,workload:,s3setup:

no_of_buckets_set=false
no_of_buckets="2"
type_of_object_MB_or_KB_set=false
type_of_object_MB_or_KB="MB"
object_size_set=false
object_size="1"
no_of_objects_set=false
no_of_objects="100"
no_of_workers_set=false
no_of_workers="2"
run_time_in_seconds_set=false
run_time_in_seconds="180"
workload_type="all"
workload_file_name=""
WORKLOAD_FILE=""
S3_SETUP_FILE=""
CONTROLLER=""
S3_SETUP_FILE="s3-setup.properties"

usage() {
  echo ""
  echo 'Usage:'
  echo '  ./run-test.sh --s3setup <s3 setup properties file> --controller <controller-ip>'
  echo '       [--interactive | --workload <workload properties file>]'
  echo ""
}

OPTS=$(getopt --options $SHORT --long $LONG  --name "$0" -- "$@")

eval set -- "$OPTS"

invalid_command() {
  printf "\nInvalid command\n"
  usage
  exit 1
}

#This function takes workload properties file as argument
parse_workload_file() {
  while IFS='=' read -r workload_option workload_value
  do
    if [ "$workload_option" == "no_of_buckets" ]
    then
      no_of_buckets=$workload_value
      no_of_buckets_set=true
    elif [ "$workload_option" == "type_of_object_MB_or_KB" ]
    then
      type_of_object_MB_or_KB=$workload_value
      type_of_object_MB_or_KB_set=true
    elif [ "$workload_option" == "object_size" ]
    then
      object_size=$workload_value
      object_size_set=true
    elif [ "$workload_option" == "no_of_objects" ]
    then
      no_of_objects=$workload_value
      no_of_objects_set=true
    elif [ "$workload_option" == "no_of_workers" ]
    then
      no_of_workers=$workload_value
      no_of_workers_set=true
    elif [ "$workload_option" == "workload_type" ]
    then
      workload_type=$workload_value
    elif [ "$workload_option" == "run_time_in_seconds" ]
    then
      run_time_in_seconds=$workload_value
      run_time_in_seconds_set=true
    else
      printf "\nInvalid option $workload_option in $1\n"
      exit 1
    fi
  done <"$1"
}

replace_placeholders() {
  while IFS=':' read -r s3setup_option s3setup_value
  do
    if [ "$s3setup_option" == "s3_endpoint" ]
    then
      s3_endpoint=$s3setup_value
    elif [ "$s3setup_option" == "access_key" ]
    then
      access_key=$s3setup_value
    elif [ "$s3setup_option" == "secret_key" ]
    then
      secret_key=$s3setup_value
    else
      printf "\nInvalid option $s3setup_option in $S3_SETUP_FILE\n"
    fi
  done <$S3_SETUP_FILE

  #Handling objects per bucket to keep total objects constant
   total_objects=$no_of_objects
   no_of_objects=$(( no_of_objects/no_of_buckets ))
   if [ $(( total_objects%no_of_buckets )) -ne 0 ]
   then
         no_of_objects=$(( no_of_objects + 1 ))
   fi

  #generate hash of 32 char
  hash=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)

  sed -i  's/_SIZE_/'"$object_size"'/g' "$workload_file_name"
  sed -i  's/_TYPE_/'"$type_of_object_MB_or_KB"'/g' "$workload_file_name"
  sed -i  's/_TOTAL_OBJECTS_/'"$total_objects"'/g' "$workload_file_name"
  sed -i  's/_OBJECTS_/'"$no_of_objects"'/g' "$workload_file_name"
  sed -i  's/_WORKERS_/'"$no_of_workers"'/g' "$workload_file_name"
  sed -i  's/_RUNTIME_/'"$run_time_in_seconds"'/g' "$workload_file_name"
  sed -i  's/_BUCKETS_/'"$no_of_buckets"'/g' "$workload_file_name"
  sed -i  's/_ACCESSKEY_/'"$access_key"'/g' "$workload_file_name"
  sed -i  "s/_SECRETKEY_/${secret_key//\//\\/}/g" "$workload_file_name"
  sed -i  "s/_S3ENDPOINT_/${s3_endpoint//\//\\/}/g"  "$workload_file_name"
  sed -i  's/_HASH_/'"$hash"'/g'  "$workload_file_name"

}

create_workload_file() {
  if [ "$workload_type" == "read" ]
  then
    workload_file_name="read_${object_size}_${type_of_object_MB_or_KB}_${no_of_buckets}_buckets_${no_of_workers}_workers.xml"
    cp read_workload_template.xml "$workload_file_name"
  elif [ "$workload_type" == "write" ]
  then
    workload_file_name="write_${object_size}_${type_of_object_MB_or_KB}_${no_of_buckets}_buckets_${no_of_workers}_workers.xml"
    cp write_workload_template.xml "$workload_file_name"
  elif [ "$workload_type" == "mixed" ]
  then
    workload_file_name="mixed_${object_size}_${type_of_object_MB_or_KB}_${no_of_buckets}_buckets_${no_of_workers}_workers.xml"
    cp mixed_workload_template.xml "$workload_file_name"
  else
    workload_file_name="all_${object_size}_${type_of_object_MB_or_KB}_${no_of_buckets}_buckets_${no_of_workers}_workers.xml"
    cp all_workload_template.xml "$workload_file_name"
  fi

  replace_placeholders
}

run_workload() {
  # Copy the workload file to conroller node
  scp "$workload_file_name" "$(whoami)"@"$CONTROLLER":/tmp
  # Run workload on controller
  result=$(ssh root@"$CONTROLLER" "cd ~/cos; sh cli.sh submit /tmp/$workload_file_name")
  if [[ $result == "Accepted"* ]]; then
    printf "\n**** Successfully launched workload ****\n"
    echo "$result"
    printf "\n***************************************\n"
  else
    echo "$result"
    printf "\nFailed to run the workload\n"
    exit 1
  fi
}



# extract options and their arguments into variables.
while true ; do
  case "$1" in
    --controller )
      CONTROLLER="$2"
      shift 2
      ;;
    --s3setup )
      S3_SETUP_FILE="$2"
      shift 2
      ;;
    --workload )
      WORKLOAD_FILE="$2"
      shift 2
      ;;
    --interactive )
      if [ "$WORKLOAD_FILE" == "" ]
      then
        read -p "Enter number of buckets:" no_of_buckets
        read -p "Enter number of objects:" no_of_objects
        read -p "Enter type of object (MB/KB):" type_of_object_MB_or_KB
        read -p "Enter object size:" object_size
        read -p "Enter number of workers:" no_of_workers
        read -p "Enter workload type:" workload_type
        read -p "Enter run time in seconds:" run_time_in_seconds
        shift
      else
        invalid-command
      fi
      ;;
    -h | --help )
      usage
      exit 0
      ;;
    -- )
      shift
      break
      ;;
    *)
      printf "$1\n"
      invalid-command
      ;;
  esac
done

if [ "$CONTROLLER" = "" ]
then
  echo
  echo "--controller option missing"
  echo
  usage
  exit 1
fi

# Print the variables
if [ "$WORKLOAD_FILE" != "" ]
then
  if [ -f "$WORKLOAD_FILE" ]
  then
    parse_workload_file "$WORKLOAD_FILE"
    if [ "$object_size_set" == false ] || [ "$no_of_buckets_set" == false ] || [ "$no_of_objects_set" == false ] ||
      [ "$no_of_workers_set" == false ] || [ "$run_time_in_seconds_set" == false ] || [ "$type_of_object_MB_or_KB_set" == false ]
    then
       printf "\nMissing option in workload properties file:$WORKLOAD_FILE\n"
       exit 1
    fi
      create_workload_file
      # Now run the workload file
      run_workload
  else
      printf "\nfile $WORKLOAD_FILE not found\n"
  fi
else
  create_workload_file
  # Now run the workload file
  run_workload
fi
