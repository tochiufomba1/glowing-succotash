export type Record = {
    Date: string;
    Number: string;
    Payee: string;
    Account: string;
    Amount: number;
    Description: string;
}

export type SummaryRecord = {
    Description: string;
    Account: string;
}

export type Option = {
    label: string;
    value: string;
};