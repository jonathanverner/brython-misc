import { EventEmitter } from 'angular2/core';
export declare class Paginator {
    rows: number;
    first: number;
    pageLinkSize: number;
    onPageChange: EventEmitter<any>;
    style: string;
    styleClass: string;
    rowsPerPageOptions: number[];
    pageLinks: number[];
    _totalRecords: number;
    totalRecords: number;
    isFirstPage(): boolean;
    isLastPage(): boolean;
    getPageCount(): number;
    calculatePageLinkBoundaries(): number[];
    updatePageLinks(): void;
    changePage(p: number): void;
    getPage(): number;
    changePageToFirst(): void;
    changePageToPrev(): void;
    changePageToNext(): void;
    changePageToLast(): void;
    onRppChange(event: any): void;
}
