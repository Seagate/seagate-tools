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
	console.log(data.columns);
	let header_row = table.insertRow();
	for (let col of data.columns)
        {
			let cell = header_row.insertCell();
			cell.appendChild(document.createTextNode(col));
			cell.setAttribute("class", TBL_HEADER_CSS);
        }

	// Populate internals
	console.log(data.data);
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
