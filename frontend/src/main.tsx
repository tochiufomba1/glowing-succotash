import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
// import App from './App.tsx'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
// import TableData from './routes/TableView.tsx'
import Upload, {action as uploadAction} from './routes/Upload.tsx';
import DownloadView from './routes/DownloadView.tsx';
import PanelParent from './PanelParent.tsx';

const router = createBrowserRouter([
  {
    path: "/",
    action: uploadAction,
    element: <Upload />,
  },
  {path: "/table",
    element: <PanelParent />
  },
  {
    path: "/download",
    element: <DownloadView />
  }
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
