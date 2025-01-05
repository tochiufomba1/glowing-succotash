import useSWR, {mutate} from 'swr';
import { SummaryRecord, Record } from './Types';
const url = 'api/dataTable';

async function updateSummaryItemRequest(id: number, data: SummaryRecord) {
  const response = await fetch(`api/updateSummary/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return response.json();
}

async function updateItemRequest(id: number, data: Record) {
  const response = await fetch(`api/updateItem/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return response.json();
}

const updateSummaryRow = async (id: number, postData: SummaryRecord) => {
  await updateSummaryItemRequest(id, postData);
  mutate(url);
};


const updateTableRow = async (id: number, postData: Record) => {
  await updateItemRequest(id, postData);
  mutate(url);
};

async function getRequest() {
  const response = await fetch(url, { credentials: 'include' })
  let result = await response.json();

  let table: Record[];
  table = JSON.parse(result.table)

  let summary: SummaryRecord[];
  summary = JSON.parse(result.summary)

  let options: string[];
  options = JSON.parse(result.options)

  const data =  {
    table: table,
    summary: summary,
    options: options
  }

  return data;
}

export default function useRecords() {
  const { data, isValidating } = useSWR(url, getRequest);
  return {
    data: data ?? [],
    isValidating,
    updateSummaryRow,
    updateTableRow
  };
}