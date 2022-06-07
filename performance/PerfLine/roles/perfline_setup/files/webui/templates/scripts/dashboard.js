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

const TBL_HEADER_CSS = "tbl_header";
const TBL_CELL_CSS = "tbl_cell";

class DashboardTableController
{
    constructor(html_table, raw_data)
    {
        this.html_table = html_table;
        this.raw_data = raw_data;
    }

    fill_table()
    {
	let table = this.html_table;
	let data = this.raw_data;

	// Populate header
	let header_row = table.insertRow();
	for (let col of data.columns)
        {
			let cell = header_row.insertCell();
			cell.appendChild(document.createTextNode(col));
			cell.setAttribute("class", TBL_HEADER_CSS);
        }

	// Populate internals
	for (let arr of data.data)
	{
        let row = table.insertRow();
		for (let el of arr)
		{
			let cell = row.insertCell();
			cell.appendChild(document.createTextNode(el));
			cell.setAttribute("class", TBL_CELL_CSS);
		}
	}
    }
}
