#!/bin/bash
#
# Seagate-tools: PerfPro
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


# Get the input parameters
INPUT_YAML_FILE=$1
YAML_PATH_FILTER=$2

# Function to parse the yaml. Each tuple is , separated
# and the vals and vals are > separated
function parseYaml
{
    s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
    sed -ne "s|^\($s\):|\1|" \
        -e "s|^\($s\)\($w\)$s:$s[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  "$1" |
    awk -F"$fs" '{
        indent = length($1)/2;
        vname[indent] = $2;
        for (i in vname) {if (i > indent) {delete vname[i]}}
        if (length($3) > 0) {
            vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])(".")}
            printf("%s%s>%s;",vn, $2, $3);
        }
    }'
}

# Check that all of the required parameters have been passed in
if [ "$INPUT_YAML_FILE" == "" ]
then
    echo "Invalid input paramters"
    echo "./parse_yaml.sh <input yaml file> [<yaml path filter> OPTIONAL]"
    echo "<input yaml file>             = $INPUT_YAML_FILE"
    echo "[<yaml path filter> OPTIONAL] = $YAML_PATH_FILTER"
    exit 1
fi

# Check if the file exists
if [ ! -f "$INPUT_YAML_FILE" ]
then
    echo "ERROR: $INPUT_YAML_FILE does not exist"
    exit 1
fi

# Store the parsed output in a single string
PARSED_OUTPUT=$(parseYaml "$INPUT_YAML_FILE")
# Remove any additional indent '.' characters
PARSED_OUTPUT=$(echo "${PARSED_OUTPUT//../.}")

# Star with empty output
OUTPUT=""

# Check if we need to do any filtering
if [ "$YAML_PATH_FILTER" == "" ]
then
    OUTPUT=$PARSED_OUTPUT
else
    # Split parsed output into an array of vars and vals
    IFS=';' read -r -a PARSED_VAR_VAL_ARRAY <<< "$PARSED_OUTPUT"
    # Loop the var val tuple array
    for VAR_VAL_ELEMENT in "${PARSED_VAR_VAL_ARRAY[@]}"
    do
        # Get the var and val from the tuple
        VAR=$(echo "$VAR_VAL_ELEMENT" | cut -f1 -d'>')
        # Check is the filter matches the var
        if [[ $VAR == $YAML_PATH_FILTER ]]
        then
            # If the OUTPUT is empty set it otherwise append
            if [ "$OUTPUT" == "" ]
            then
                OUTPUT=$VAR_VAL_ELEMENT
            else
                OUTPUT=$OUTPUT";"$VAR_VAL_ELEMENT
            fi
        fi
    done
fi

# Return the parsed output
echo "$OUTPUT"
