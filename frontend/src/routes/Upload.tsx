// import React, { useState } from "react"
// import { useState } from "react";
import  { useState } from "react";
import "../Upload.css"
// import { Navigate } from "react-router-dom"

import { Form, redirect, useSubmit } from "react-router-dom";

export async function action(props: any) {
    const { request } = props;
    const formData = await request.formData();

    const actionRequest = new Request("api/upload", {
        method: "POST",
        credentials: "include",
        body: formData,
    });

    const actionResponse = await fetch(actionRequest);
    if (!actionResponse.ok) {
        console.log("here " + actionResponse.body + " " + actionResponse.statusText);
        throw new Error(`Response status: ${actionResponse.status}`);
    }

    return redirect(`/table`)

    // fetch
    // check if response is ok
    // redirect to basic tab or report page
}

export default function Upload() {
    const [loading, setLoading] = useState(false)
    const submit = useSubmit();

    const handleSubmit = (event) => {
        event.preventDefault();
        setLoading(true)

        // const formData = new FormData(event.target);
        // const data = Object.fromEntries(formData);

        submit(event.currentTarget, { action: '/' });
    };
    // const handleClick = () => {
    //     setLoading(true)
    //     useSubmit();
    // }

    return (
        <div className="form">
            <h1>File Upload</h1>
            <Form onSubmit={handleSubmit} method="post" encType="multipart/form-data" style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                <input type="file" name="file" accept=".csv, .xlsx" required />
                <label htmlFor="business">Business</label>
                <select name="business" id="business">
                    <option value="4 Ever Young">4 Ever Young</option>
                    <option value="New Knowledge">New Knowledge</option>
                    <option value="Nucare">Nucare</option>
                </select>
                <button type="submit" disabled={loading} >Submit</button> 
            </Form>
            {loading == true && <h2>Loading...</h2>}
        </div>
    )
}

// export default function Upload() {
//     const [file, setFile] = useState<File | null>(null)
//     const [fileUploaded, setFileUploaded] = useState(false)
//     // const [loading, setLoading] = useState(false)

//     const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
//         const files = e.currentTarget.files;
//         if (files)
//             setFile(files[0])
//     }

//     const  handleSubmit = async (_e: React.FormEvent<HTMLFormElement>) => {
//         const formData = new FormData()
//         if (file) {
//             formData.append('file', file)
//         }

//         try {
//             const response = await fetch("http://localhost:5000/api/upload" , {method: "POST", headers: { "Content-Type": "multipart/form-data" }, body: formData })
//             console.log("hew")
//             if (response.status === 200){
//                 setFileUploaded(true)
//             }

//         } catch (error: unknown) {
//             console.error(error);
//         }
//     }

//     return (
//         <>
//             {fileUploaded && (<Navigate to="/table"/>)}

//             <div className="form">
//                 <h1>File Upload</h1>
//                 <form onSubmit={handleSubmit}>
//                     <input type="file" name="file" accept=".csv, .xlsx" required onChange={handleFileInput} />
//                     <button>Submit</button>
//                 </form>
//             </div>
//         </>
//     )
// }