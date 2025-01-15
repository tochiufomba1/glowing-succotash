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
import useRecords from './useRecords';

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
    const { data: originalData, isValidating, updateSummaryRow, updateTableRow } = useRecords();
    const [dataFrame, setDataFrame] = useState<Record[]>([]);
    const [dataFrame2, setDataFrame2] = useState<SummaryRecord[]>([]);
    const [options, setOptions] = useState<string[]>([]);
    const [value, setValue] = useState(0);

    const handleChange = (_event: React.SyntheticEvent, newValue: number) => {
        setValue(newValue);
    };

    const navigate = useNavigate();

    const handleExport = () => {
        navigate("/download")
    }

    useEffect(() => {
        if (isValidating) {
            return;
        }

        setDataFrame((_dataFrame) => originalData["table"])
        setDataFrame2((_dataFrame2) => originalData["summary"])
        setOptions((_options) => originalData["options"])
        // console.log(originalData)

    }, [isValidating]);

    if (dataFrame && dataFrame2 && options) {
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
                        <TableView data={dataFrame} setData={setDataFrame} optionsList={options} updateRow={updateTableRow} />
                    </CustomTabPanel>
                    <CustomTabPanel value={value} index={1}>
                        <SummaryView data={dataFrame2} setData={setDataFrame2} optionsList={options} updateRow={updateSummaryRow} />
                    </CustomTabPanel>
                </Box>
            </>
        )
    }

    // return (isValidating == false &&
    //     <>
    //         <Box sx={{ width: '100%' }}>
    //             <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
    //                 <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
    //                     <Tab label="Table" {...a11yProps(0)} />
    //                     <Tab label="Summary" {...a11yProps(1)} />
    //                     <UploadButton handleExport={handleExport} />
    //                 </Tabs>
    //             </Box>
    //             <CustomTabPanel value={value} index={0}>
    //                 <TableView data={dataFrame} setData={setDataFrame} />
    //             </CustomTabPanel>
    //             <CustomTabPanel value={value} index={1}>
    //                 <SummaryView data={dataFrame2} setData={setDataFrame2} />
    //             </CustomTabPanel>
    //         </Box>
    //     </>
    // )
}