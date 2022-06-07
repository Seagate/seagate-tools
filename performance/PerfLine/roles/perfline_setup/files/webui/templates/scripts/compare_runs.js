/*
* Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU Affero General Public License as published
* by the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU Affero General Public License for more details.
* You should have received a copy of the GNU Affero General Public License
* along with this program. If not, see <https://www.gnu.org/licenses/>.
*
* For any questions about this software or licensing,
* please email opensource@seagate.com or cortx-questions@seagate.com.
*
* -*- coding: utf-8 -*-
*/

"use strict";

const HIGHLIGHT_DIFF_PERCENT = 3;
const ROUND_DIGITS_AFTER_POINT = 3;

const BLACK_TEXT_CSS = "black_text";
const GREEN_TEXT_CSS = "green_text";
const RED_TEXT_CSS = "red_text";

function round_number(value)
{
    if (!isNaN(value))
    {
        value = (+value).toFixed(ROUND_DIGITS_AFTER_POINT);
        value = +value;
    }

    return value;
}

function compare_with_base_value(base_val, value, metric_name)
{
    let difference = 0;
    let result = 0;
    let sign = 1;

    for (let m of ["TTFB","ERRORS", "DURATION"])
    {
        if (metric_name.toUpperCase().indexOf(m) !== -1)
        {
            sign = -1;
            break;
        }
    }

    if (isNaN(base_val) || isNaN(value) || base_val === null || value === null)
    {
        var data = {
            result: result,
            difference: difference,
        };
        return data;
    }

    // string to number
    let base_val_number = +base_val;
    let val_number = +value;

    difference = ((val_number / base_val_number) - 1) * 100;
    difference = difference.toFixed();

    if (difference < -HIGHLIGHT_DIFF_PERCENT)
    {
        result = -1 * sign;
    }
    else if(difference > HIGHLIGHT_DIFF_PERCENT)
    {
        result = 1 * sign;
    }

    return {result: result, difference: difference};
}

class BaseTableController
{
    constructor(html_table, raw_data)
    {
        this.html_table = html_table;
        this.tasks_benchmarks_results = raw_data;
    }

    find_metrics()
    {
        this.metrics = new Array();

        for (let key in this.tasks_benchmarks_results[0].benchmarks[0].metrics)
        {
            if (this.displayed_metrics !== undefined)
            {
                for (let metric_name_template of this.displayed_metrics)
                {
                    if (key.toUpperCase().indexOf(metric_name_template) !== -1)
                    {
                        this.metrics.push(key);
                        break;
                    }
                }
            }
            else
            {
                this.metrics.push(key);
            }
        }
    }

    find_task_ids()
    {
        this.task_ids = new Array();

        for (let task_data of this.tasks_benchmarks_results)
        {
            this.task_ids.push(task_data.task_id);
        }
    }

    find_tasks_metadata()
    {
        this.tasks_metadata = new Map();

        for (let task_data of this.tasks_benchmarks_results)
        {
            this.tasks_metadata.set(task_data.task_id, task_data.metadata);
        }
    }

    workloads_order_equal()
    {
        let same_order = true;
        let workloads_nr = this.tasks_benchmarks_results[0].benchmarks.length;

        for (let task_data of this.tasks_benchmarks_results)
        {
            if (task_data.benchmarks.length !== workloads_nr)
            {
                same_order = false;
                break;
            }

            for (let i = 0; i < workloads_nr; ++i)
            {
                if (task_data.benchmarks[i].workload !== this.tasks_benchmarks_results[0].benchmarks[i].workload)
                {
                    same_order = false;
                    break;
                }
            }

            if (!same_order)
            {
                break;
            }
        }

        return same_order;
    }

    match_workloads_in_original_order()
    {
        let workloads_nr = this.tasks_benchmarks_results[0].benchmarks.length

        for (let i = 0; i < workloads_nr; ++i)
        {
            let workload = this.tasks_benchmarks_results[0].benchmarks[i].workload;
            let tmp_obj = {
                workload: workload
            };

            for (let task_data of this.tasks_benchmarks_results)
            {
                tmp_obj[task_data.task_id] = task_data.benchmarks[i].metrics;
            }

            this.benchmark_results.push(tmp_obj);
        }
    }

    match_workloads_between_tasks()
    {
        let all_workloads = new Set();

        // collect all available workloads
        for (let task_benchmarks of this.tasks_benchmarks_results)
        {
            for (let task_benchmark of task_benchmarks.benchmarks)
            {
                all_workloads.add(task_benchmark.workload);
            }
        }

        let tmp_results = new Map();

        for (let task_benchmarks of this.tasks_benchmarks_results)
        {
            let workloads_metrics = new Map();
            for (let task_benchmark of task_benchmarks.benchmarks)
            {
                let workload_name = task_benchmark.workload;
                if (!workloads_metrics.has(workload_name))
                {
                    workloads_metrics.set(workload_name, new Array());
                }

                workloads_metrics.get(workload_name).push(task_benchmark.metrics);
            }

            tmp_results.set(task_benchmarks.task_id, workloads_metrics);
        }

        for (let workload of all_workloads)
        {
            let iteration = -1;
            let need_next_iteration = true;

            while(need_next_iteration)
            {
                need_next_iteration = false;
                iteration++;

                let tmp_obj = {
                    workload: workload,
                    iteration: iteration
                };

                for (let task_id of this.task_ids)
                {
                    let task_results = tmp_results.get(task_id);
                    if (task_results.has(workload) && task_results.get(workload).length > iteration)
                    {
                        if (task_results.get(workload).length > (iteration + 1))
                        {
                            need_next_iteration = true;
                        }

                        tmp_obj[task_id] = task_results.get(workload)[iteration];
                    }
                    else
                    {
                        tmp_obj[task_id] = null;
                    }
                }

                this.benchmark_results.push(tmp_obj);
            }
        }
    }

    prepare_data()
    {
        if (this.tasks_benchmarks_results.length === 0)
        {
            return;
        }

        this.benchmark_results = new Array();

        this.find_metrics();
        this.find_task_ids();
        this.find_tasks_metadata();

        if (this.workloads_order_equal())
        {
            this.match_workloads_in_original_order();
        }
        else
        {
            this.match_workloads_between_tasks();
        }
    }
}

class SummaryTableController extends BaseTableController
{
    constructor(html_table, raw_data)
    {
        super(html_table, raw_data);
        this.displayed_metrics = ["ERRORS", "THROUGHPUT"];
    }

    create_header_row()
    {
        let row = this.html_table.insertRow();

        let cell = row.insertCell();
        cell.appendChild(document.createTextNode("task id"));

        for (let task_id of this.task_ids)
        {
            let cell = row.insertCell();
            cell.appendChild(document.createTextNode(task_id));
            cell.setAttribute("colspan", this.metrics.length);
            cell.setAttribute("class", BLACK_TEXT_CSS);
        }
    }

    create_tasks_metadata_row()
    {
        let row = this.html_table.insertRow();

        let cell = row.insertCell();
        cell.appendChild(document.createTextNode(""));

        for (let task_id of this.task_ids)
        {
            let md_str = "";
            for (let md_val in this.tasks_metadata.get(task_id))
            {
                md_str += `${md_val}: ${this.tasks_metadata.get(task_id)[md_val]}\n`;
            }
            let cell = row.insertCell();
            cell.appendChild(document.createTextNode(md_str));
            cell.setAttribute('colspan', this.metrics.length);
            cell.setAttribute("class", BLACK_TEXT_CSS);
        }
    }

    create_metrics_row()
    {
        let row = this.html_table.insertRow();

        let cell = row.insertCell();
        cell.appendChild(document.createTextNode("workload"));

        for (let i = 0; i < this.task_ids.length; ++i)
        {
            for (let metric_name of this.metrics)
            {
                let cell = row.insertCell();
                cell.appendChild(document.createTextNode(metric_name));
                cell.setAttribute("class", BLACK_TEXT_CSS);
            }
        }
    }

    create_results_row(res)
    {
        let row = this.html_table.insertRow();

        let cell = row.insertCell();
        cell.appendChild(document.createTextNode(res.workload.replaceAll(",", "\n")));
        cell.setAttribute("class", BLACK_TEXT_CSS);

        let metric_baseval_map = new Map();
        for (let metric_name of this.metrics)
        {
            //get base values
            let base_val = res[this.task_ids[0]]?.[metric_name];
            metric_baseval_map.set(metric_name, base_val);
        }

        for (let task_id of this.task_ids)
        {
            for (let metric_name of this.metrics)
            {
                let cell = row.insertCell();
                let val  = "---";
                let css_class = BLACK_TEXT_CSS;

                let task_results = res[task_id];

                if(task_results !== null && task_results[metric_name] !== undefined)
                {
                    val = task_results[metric_name];
                    let base_val = metric_baseval_map.get(metric_name);
                    let diff = compare_with_base_value(base_val, val, metric_name);
                    val = round_number(val);

                    if (diff.result > 0)
                    {
                        css_class = GREEN_TEXT_CSS;
                        val = `${val} (${diff.difference}%)`;
                    }
                    else if (diff.result < 0)
                    {
                        css_class = RED_TEXT_CSS;
                        val = `${val} (${diff.difference}%)`;
                    }
                }

                cell.appendChild(document.createTextNode(val));
                cell.setAttribute("class", BLACK_TEXT_CSS);
                cell.setAttribute("class", css_class);
            }
        }
    }

    fill_table()
    {
        this.prepare_data();
        this.create_header_row();
        this.create_tasks_metadata_row();
        this.create_metrics_row();

        for (let res of this.benchmark_results)
        {
            this.create_results_row(res);
        }
    }
}

class DetailedTableController extends BaseTableController
{
    constructor(html_table, raw_data)
    {
        super(html_table, raw_data);
    }

    prepare_metric_row_data(res, metric_name)
    {
        let columns_vals = new Array();
        columns_vals.push(metric_name);

        let base_val = res[this.task_ids[0]]?.[metric_name];

        for (let task of this.task_ids)
        {
            let task_results = res[task];

            if (task_results === null || task_results[metric_name] === undefined)
            {
                columns_vals.push({text: "---", css_class: BLACK_TEXT_CSS});
            }
            else
            {
                let value = task_results[metric_name];
                let diff = compare_with_base_value(base_val, value, metric_name);
                value = round_number(value);

                let css_class = BLACK_TEXT_CSS;
                if (diff.result > 0)
                {
                    css_class = GREEN_TEXT_CSS;
                    value = `${value} (${diff.difference}%)`;
                }
                else if (diff.result < 0)
                {
                    css_class = RED_TEXT_CSS;
                    value = `${value} (${diff.difference}%)`;
                }

                columns_vals.push({
                    text: value,
                    css_class: css_class
                });
            }
        }

        return columns_vals;
    }

    create_workload_row(workload_str)
    {
        let row = this.html_table.insertRow();
        let cell = row.insertCell();
        cell.appendChild(document.createTextNode("workload"));
        cell = row.insertCell();
        let text_node = document.createTextNode(workload_str);
        cell.appendChild(text_node);
        cell.setAttribute("colspan", this.task_ids.length);
        cell.setAttribute("class", BLACK_TEXT_CSS);
    }

    create_task_ids_row()
    {
        let row = this.html_table.insertRow();
        let cell = row.insertCell();
        cell.appendChild(document.createTextNode("task id"));

        for (let task_id of this.task_ids)
        {
            cell = row.insertCell();
            let text_node = document.createTextNode(task_id);
            cell.appendChild(text_node);
            cell.setAttribute("class", BLACK_TEXT_CSS);
        }
    }

    fill_table()
    {
        this.prepare_data();

        for (let res of this.benchmark_results)
        {
            this.create_workload_row(res.workload);
            this.create_task_ids_row();

            for (let metric_name of this.metrics)
            {
                let columns_vals = this.prepare_metric_row_data(res, metric_name);
                create_row(this.html_table, columns_vals);
            }
        }
    }
}

function create_row(table, columns)
{
    let row = table.insertRow();

    for (let column_text of columns)
    {
        let cell = row.insertCell();
        let tmp_str = column_text;
        if (typeof(column_text) == "object")
        {
            tmp_str = column_text.text;
            if (column_text.css_class !== undefined)
            {
                cell.setAttribute("class", column_text.css_class);
            }
        }

        let newText = document.createTextNode(tmp_str);
        cell.appendChild(newText);
    }
}

function request_data_from_api(method_name, task_ids)
{
    let result = null;
    let get_params = "?";

    for (let tid of task_ids)
    {
        get_params += `task_id=${tid}&`;
    }

    let http_req = new XMLHttpRequest();
    http_req.open("GET", `/api/${method_name}${get_params}`, false);
    http_req.onload = () => {
        if (http_req.status === 200)
        {
            result = JSON.parse(http_req.response);
        }
    };
    http_req.send();
    return result;
}

function request_metadata(task_ids)
{
    return request_data_from_api("get_tasks_metadata", task_ids);
}

function request_perf_metrics(task_ids)
{
    return request_data_from_api("get_perf_metrics", task_ids);
}

document.addEventListener("DOMContentLoaded", () => {

    let task_id_inputs = document.getElementsByName("task_id_value");
    let task_ids = new Array();

    for (let tid_input of task_id_inputs)
    {
        task_ids.push(tid_input.value);
    }

    if (task_ids.length === 0)
    {
        alert("task list is empty");
        return;
    }

    // load tasks metadata
    let tasks_metadata = request_metadata(task_ids);

    if (tasks_metadata === null)
    {
        alert("tasks metadata loading error");
        return;
    }

    // load tasks performance data
    let perf_metrics = request_perf_metrics(task_ids);

    if (perf_metrics === null)
    {
        alert("tasks performance data loading error");
        return;
    }

    // combine all data (metadata + perf metrics) in a single object
    let tmp_map = new Map();
    let data = new Array();

    for (let obj of tasks_metadata)
    {
        tmp_map.set(obj.task_id, {task_id: obj.task_id, metadata: obj.metadata});
    }

    for (let obj of perf_metrics)
    {
        tmp_map.get(obj.task_id).benchmarks = obj.benchmarks;
    }

    for (let tid of task_ids)
    {
        data.push(tmp_map.get(tid));
    }

    let ctrl = new DetailedTableController(document.getElementById("data_table"), data);
    ctrl.fill_table();

    ctrl = new SummaryTableController(document.getElementById("summary_table"), data);
    ctrl.fill_table();
});
