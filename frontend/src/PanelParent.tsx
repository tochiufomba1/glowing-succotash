import { Box } from '@mui/material';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import SummaryView from './routes/SummaryView';
import TableView from './routes/TableView';
import { useEffect, useState } from 'react';
import { Record } from './Types';
import { SummaryRecord } from './Types';
import UploadButton from './UploadButton';
import { useNavigate } from "react-router-dom";

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function CustomTabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`simple-tabpanel-${index}`}
            aria-labelledby={`simple-tab-${index}`}
            {...other}
        >
            {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
        </div>
    );
}

function a11yProps(index: number) {
    return {
        id: `simple-tab-${index}`,
        'aria-controls': `simple-tabpanel-${index}`,
    };
}

export default function PanelParent() {
    const [dataFrame, setDataFrame] = useState<Record[]>();
    const [dataFrame2, setDataFrame2] = useState<SummaryRecord[]>();
    const [options, setOptions] = useState<string[]>([]);
    const [value, setValue] = useState(0);

    const handleChange = (_event: React.SyntheticEvent, newValue: number) => {
        setValue(newValue);
    };

    const navigate = useNavigate();

    const handleExport = async () => {
        const finalData = {
            tableData: dataFrame,
            summaryData: dataFrame2
        }

        // send updated data to backend
        const response = await fetch(`api/export`, { method: "POST", headers: { "Content-Type": "application/json", }, body: JSON.stringify(finalData), credentials: 'include' })
        if (!response.ok) {
            // error
            console.log("error")
        } else {
            try {
                // const response = await fetch('/download_excel');
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', 'labeledData.xlsx');
                document.body.appendChild(link);
                link.click();
                navigate("/download")
            } catch (error) {
                console.error('Error downloading file:', error);
            }
        }
    }

    useEffect(() => {
        const fetchData = async () => {
            // fetch pandas dataframe from backend
            const response = await fetch(`api/dataTable`, { credentials: 'include' })
            const result = await response.json()
            // console.log(result)
            let x = JSON.parse(result.table)
            let y = JSON.parse(result.summary)
            let z = JSON.parse(result.options)
            console.log(z)
            setDataFrame((_dataFrame) => x)
            setDataFrame2((_dataFrame2) => y)
            setOptions((_options) => z)
            // console.log("fhwo: " + Array.isArray([x]))
        }

        fetchData();

    }, []);

    return (
        <>
            <Box sx={{ width: '100%' }}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
                        <Tab label="Table" {...a11yProps(0)} />
                        <Tab label="Summary" {...a11yProps(1)} />
                        <UploadButton handleExport={handleExport} />
                    </Tabs>
                </Box>
                <CustomTabPanel value={value} index={0}>
                    <TableView data={dataFrame} setData={setDataFrame} COAoptions={options}  />
                </CustomTabPanel>
                <CustomTabPanel value={value} index={1}>
                    <SummaryView data={dataFrame2} setData={setDataFrame2} COAoptions={options} />
                </CustomTabPanel>
            </Box>
        </>
    )
}