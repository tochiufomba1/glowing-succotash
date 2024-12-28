import { useCallback, useEffect, useRef, useState } from "react";
import "../TableView.css"
import { Record, Option } from "../Types.ts"
import {
    createColumnHelper,
    flexRender,
    getCoreRowModel,
    useReactTable,
    getPaginationRowModel,
} from '@tanstack/react-table'

let options = []
// import { useNavigate } from "react-router-dom";

// type Record = {
//     Date: string;
//     Number: string;
//     Payee: string;
//     Account: string;
//     Amount: number;
//     Description: string;
// }

const EditCell = ({ row, table }) => {
    const meta = table.options.meta;
    const validRow = meta?.validRows[row.id];
    const disableSubmit = validRow ? Object.values(validRow)?.some(item => !item) : false;

    const setEditedRows = (e: React.MouseEvent<HTMLButtonElement>) => {
        const elName = e.currentTarget.name
        meta?.setEditedRows((old: []) => ({
            ...old,
            [row.id]: !old[row.id],
        }))

        if (elName !== "edit") {
            meta?.revertData(row.index, e.currentTarget.name === "cancel")
        }
    }

    return meta?.editedRows[row.id] ? (
        <>
            <button onClick={setEditedRows} name="cancel">
                X
            </button>{" "}
            <button onClick={setEditedRows} name="done" disabled={disableSubmit}>
                ✔
            </button>
        </>
    ) : (
        <button onClick={setEditedRows} name="edit">
            ✐
        </button>
    )
}

const TableCell = ({ getValue, row, column, table }) => {
    const initialValue = getValue();
    const columnMeta = column.columnDef.meta;
    const tableMeta = table.options.meta;
    const [value, setValue] = useState(initialValue)

    useEffect(() => {
        setValue(initialValue)
    }, [initialValue])

    const onBlur = (e: React.ChangeEvent<HTMLInputElement>) => {
        tableMeta?.updateData(row.index, column.id, value, e.target.validity.valid)
    }

    const onSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setValue(e.target.value);
        tableMeta?.updateData(row.index, column.id, e.target.value);
    };

    if (tableMeta?.editedRows[row.id]) {
        return columnMeta?.type === "select" ? (
            <select onChange={onSelectChange} value={initialValue}>
                {columnMeta?.options?.map((option: Option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                ))}
            </select>
        ) : (
            <input
                value={value}
                onChange={(e) => setValue(e.target.value)}
                onBlur={onBlur}
                type={columnMeta?.type || "text"}
                required={columnMeta?.required}
            />
        );
    }
    return <span>{value}</span>
}

const columnHelper = createColumnHelper<Record>();

const columns = [
    columnHelper.accessor("Date", {
        header: "Date",
        cell: TableCell,
        meta: {
            type: "date",
            required: true,
        }
    }),
    columnHelper.accessor("Number", {
        header: "Number",
        cell: TableCell,
        meta: {
            type: "number",
            required: false,
        }
    }),
    columnHelper.accessor("Payee", {
        header: "Payee",
        cell: TableCell,
        meta: {
            type: "text",
            required: false,
        }
    }),
    columnHelper.accessor("Account", {
        header: "Account",
        cell: TableCell,
        meta: {
            type: "select",
            options: options.map((item) => ({ value: item, label: item })),
            required: false,
        }
    }),
    columnHelper.accessor("Amount", {
        header: "Amount",
        cell: TableCell,
        meta: {
            type: "number",
            required: false,
        }
    }),
    columnHelper.accessor("Description", {
        header: "Description",
        cell: TableCell,
        meta: {
            type: "text",
            required: true,
        }
    }),
    columnHelper.display({
        id: "edit",
        cell: EditCell
    })
];

export default function TableData({ data, setData, COAoptions }) {
    useEffect(() => {
        options = COAoptions;
        console.log('Global variable:', options);
    }, [COAoptions]);
    // const [dataFrame, setDataFrame] = useState<Record[]>();

    // setDataFrame((_dataFrame) => data)

    // useEffect(() => {
    //     const fetchData = async () => {
    //         // fetch pandas dataframe from backend
    //         const response = await fetch(`api/dataTable`, { credentials: 'include' })
    //         const result = await response.json()
    //         const x = JSON.parse(result)
    //         console.log(x)
    //         setDataFrame((_dataFrame) => x)

    //         console.log("fhwo: " + Array.isArray([x]))
    //     }

    //     fetchData();

    // }, []);

    return (data && <TableUnstyled data={data} setData={setData} />)
}

function TableUnstyled({ data, setData }) {
    // const { dataFrame } = props
    // // const navigate = useNavigate();
    // const [data, setData] = useState(() => [...dataFrame])
    const [originalData, setOriginalData] = useState(() => [...data]);
    const [editedRows, setEditedRows] = useState({});
    const [validRows, setValidRows] = useState({});

    // const handleExport = async () => {
    //     // send updated data to backend
    //     const response = await fetch(`api/export`, { method: "POST", headers: { "Content-Type": "application/json", }, body: JSON.stringify(data), credentials: 'include' })
    //     if (!response.ok) {
    //         // error
    //         console.log("error")
    //     }
    //     else {
    //         try {
    //             // const response = await fetch('/download_excel');
    //             const blob = await response.blob();
    //             const url = window.URL.createObjectURL(blob);
    //             const link = document.createElement('a');
    //             link.href = url;
    //             link.setAttribute('download', 'labeledData.xlsx');
    //             document.body.appendChild(link);
    //             link.click();
    //             navigate("/download")
    //         } catch (error) {
    //             console.error('Error downloading file:', error);
    //         }

    //         // transfer to other page
    //         // const rep =  await response.json();
    //         // const filename = rep["filename"];
    //         // const state = { file: filename };
    //         // navigate("/download")
    //         // console.log(filename);
    //         // <Navigate to={`/download`} state={filename} replace={true} />
    //     }
    // }

    const [autoResetPageIndex, skipAutoResetPageIndex] = useSkipper()

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        autoResetPageIndex,
        meta: {
            validRows,
            setValidRows,
            editedRows,
            setEditedRows,
            revertData: (rowIndex: number, revert: boolean) => {
                if (revert) {
                    skipAutoResetPageIndex()
                    setData((old) =>
                        old.map((row, index) =>
                            index === rowIndex ? originalData[rowIndex] : row
                        )
                    );
                } else {
                    setOriginalData((old) =>
                        old.map((row, index) => (index === rowIndex ? data[rowIndex] : row))
                    );
                }
            },
            updateData: (rowIndex: number, columnId: string, value: string, isValid: boolean) => {
                skipAutoResetPageIndex()
                setData((old) =>
                    old.map((row, index) => {
                        if (index === rowIndex) {
                            return {
                                ...old[rowIndex],
                                [columnId]: value,
                            };
                        }
                        return row;
                    })
                );
                setValidRows((old) => ({
                    ...old,
                    [rowIndex]: { ...old[rowIndex], [columnId]: isValid },
                }));
            },
        },
    });

    return (
        <>
            {/* <button onClick={handleExport}>Upload</button> */}
            <table aria-label="custom pagination table">
                <thead>
                    {table.getHeaderGroups().map((headerGroup) => (
                        <tr key={headerGroup.id}>
                            {headerGroup.headers.map((header) => (
                                <th key={header.id}>
                                    {header.isPlaceholder
                                        ? null
                                        : flexRender(
                                            header.column.columnDef.header,
                                            header.getContext()
                                        )}
                                </th>
                            ))}
                        </tr>
                    ))}
                </thead>
                <tbody>
                    {table.getRowModel().rows.map((row) => (
                        <tr key={row.id}>
                            {row.getVisibleCells().map((cell) => (
                                <td key={cell.id}>
                                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
                {/* <tfoot>
                    <tr>
                        <CustomPaginationComponent
                            count={dataFrame?.length}
                            rowsPerPage={rowsPerPage}
                            page={page}
                            onPageChange={handleChangePage}
                        />
                    </tr>
                </tfoot> */}
            </table>
            <div className="flex items-center gap-2" style={{ display: "flex", alignItems: "center", gap: 2 }}>
                <button
                    className="border rounded p-1"
                    onClick={() => table.setPageIndex(0)}
                    disabled={!table.getCanPreviousPage()}
                >
                    {'<<'}
                </button>
                <button
                    className="border rounded p-1"
                    onClick={() => table.previousPage()}
                    disabled={!table.getCanPreviousPage()}
                >
                    {'<'}
                </button>
                <button
                    className="border rounded p-1"
                    onClick={() => table.nextPage()}
                    disabled={!table.getCanNextPage()}
                >
                    {'>'}
                </button>
                <button
                    className="border rounded p-1"
                    onClick={() => table.setPageIndex(table.getPageCount() - 1)}
                    disabled={!table.getCanNextPage()}
                >
                    {'>>'}
                </button>
                <span className="flex items-center gap-1">
                    <div>Page</div>
                    <strong>
                        {table.getState().pagination.pageIndex + 1} of{' '}
                        {table.getPageCount()}
                    </strong>
                </span>
                <span className="flex items-center gap-1">
                    | Go to page:
                    <input
                        type="number"
                        min="1"
                        max={table.getPageCount()}
                        defaultValue={table.getState().pagination.pageIndex + 1}
                        onChange={e => {
                            const page = e.target.value ? Number(e.target.value) - 1 : 0
                            table.setPageIndex(page)
                        }}
                        className="border p-1 rounded w-16"
                    />
                </span>
                <select
                    value={table.getState().pagination.pageSize}
                    onChange={e => {
                        table.setPageSize(Number(e.target.value))
                    }}
                >
                    {[10, 20, 30, 40, 50].map(pageSize => (
                        <option key={pageSize} value={pageSize}>
                            Show {pageSize}
                        </option>
                    ))}
                </select>
            </div>
            <div>{table.getRowModel().rows.length} Rows</div>
        </>
    );
}

// function Row(props: any) {
//     const { item } = props;

//     // const data = Object.keys(item)
//     return (
//         <tr>
//             <td>{item.Date}</td>
//         </tr>
//     )
// }

// const CustomPaginationComponent = (props: any) => {
//     const { page, rowsPerPage, count, onPageChange } = props;
//     let from = rowsPerPage * page + 1;
//     let to = rowsPerPage * (page + 1);
//     if (to > count) {
//         to = count;
//     }
//     return (
//         <td>
//             <div style={{ display: 'flex', justifyContent: 'center' }}>
//                 <div>
//                     <button disabled={page === 0} onClick={(e) => onPageChange(e, page - 1)}>Prev</button>
//                 </div>

//                 <div>
//                     <h4>
//                         {from}-{to} of {count} transactions
//                     </h4>
//                 </div>
//                 <div>
//                     <button disabled={to >= count} onClick={(e) => onPageChange(e, page + 1)}>Next</button>
//                 </div>
//             </div>
//         </td>
//     );
// }

function useSkipper(): [any, any] {
    const shouldSkipRef = useRef(true)
    const shouldSkip = shouldSkipRef.current

    // Wrap a function with this to skip a pagination reset temporarily
    const skip = useCallback(() => {
        shouldSkipRef.current = false
    }, [])

    useEffect(() => {
        shouldSkipRef.current = true
    })

    return [shouldSkip, skip] as const
}