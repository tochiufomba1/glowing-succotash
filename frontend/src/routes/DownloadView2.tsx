import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function TaskComponent() {
    const [taskId, setTaskId] = useState(null);
    const [status, setStatus] = useState("pending")

    const submitTask = async () => { 
        const response = await fetch(`api/export`, { credentials: 'include' });
        const resp = await response.json();
    
        setTaskId(resp["job_id"]); 
    }

    useEffect(() => {
        if (taskId) {
            const interval = setInterval(async () => {
                const response = await fetch(`api/export/${taskId}`);
                if (response.ok) {
                    try {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const link = document.createElement('a');
                        link.href = url;
                        link.setAttribute('download', 'labeledData.xlsx');
                        document.body.appendChild(link);
                        link.click();
                        setStatus("complete")
                    } catch (error) {
                        console.error('Error downloading file:', error);
                    }
                    clearInterval(interval);
                }
            }, 2000); // Poll every 2 seconds 

            return () => clearInterval(interval);
        }
        else{
            submitTask()
        }
    }, [taskId]);

    if (status === "complete") {
        return (
            <>
                <h1>Download Complete</h1>
                <Link to="/">Upload more files here</Link>
            </>
        )
    }

    return <h1>Downloading...</h1>
}