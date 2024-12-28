// import { useEffect } from "react";
// import { useEffect } from "react";
// import { Link, useLocation } from "react-router-dom";
// // import { saveAs } from 'file-saver'
// import axios, { AxiosRequestConfig } from "axios";

import { Link } from "react-router-dom";

// export async function loader({ params }) {
//     const filename = params.filename;
//     return filename;
// }

export default function DownloadView() {
    // const filename = useLocation().state;
    // const location = useLocation();
    // const { state } = location;

    // useEffect(() => {
    //     const downloadFile = async (filename) => {
    //         const headers = { 'Content-Type': 'blob' };
    //         const config: AxiosRequestConfig = { method: 'GET', url:`downloads/${filename}`, responseType: 'arraybuffer', headers };

    //         try {
    //             const response = await axios(config);

    //             const outputFilename = filename;

    //             // If you want to download file automatically using link attribute.
    //             const url = URL.createObjectURL(new Blob([response.data]));
    //             const link = document.createElement('a');
    //             link.href = url;
    //             link.setAttribute('download', outputFilename);
    //             document.body.appendChild(link);
    //             link.click();

    //         } catch (error) {
    //             console.log(error);
    //         }
    //         // axios.post(`downloads/${filename}`, {
    //         //     method: 'GET',
    //         //     responseType: 'blob', // important
    //         // }).then((response) => {
    //         //     const url = window.URL.createObjectURL(new Blob([response.data]));
    //         //     const link = document.createElement('a');
    //         //     link.href = url;
    //         //     link.setAttribute('download', `${filename}`);
    //         //     document.body.appendChild(link);
    //         //     link.click();
    //         // });
    //     }

    //     downloadFile(state.file)
    // }, [])

    return (
        <>
            <h1>Download</h1>
            <Link to="/">Upload more files here</Link>
        </>
    )
}