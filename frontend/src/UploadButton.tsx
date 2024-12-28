export default function UploadButton({handleExport}){
    // const navigate = useNavigate();
    // const finalData = 
    // {
    //     tableData: data,
    //     summaryData: summaryData
    // }
    
    // const handleExport = async () => {
    //     // send updated data to backend
    //     const response = await fetch(`api/export`, { method: "POST", headers: { "Content-Type": "application/json", }, body: JSON.stringify(finalData), credentials: 'include' })
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

    return (
        <button onClick={handleExport}>Upload</button>
    )
}