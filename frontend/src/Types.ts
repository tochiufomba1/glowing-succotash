export type Record = {
    index: number;
    Date: string;
    Number: string;
    Payee: string;
    Account: string;
    Amount: number;
    Description: string;
}

export type SummaryRecord = {
    index: number,
    Description: string;
    Account: string;
}

export type Option = {
    label: string;
    value: string;
};