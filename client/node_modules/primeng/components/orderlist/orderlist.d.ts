import { ElementRef, TemplateRef, EventEmitter } from '@angular/core';
import { DomHandler } from '../dom/domhandler';
export declare class OrderList {
    private el;
    private domHandler;
    value: any[];
    header: string;
    style: any;
    styleClass: string;
    listStyle: any;
    responsive: boolean;
    onReorder: EventEmitter<any>;
    itemTemplate: TemplateRef<any>;
    constructor(el: ElementRef, domHandler: DomHandler);
    onMouseover(event: any): void;
    onMouseout(event: any): void;
    onClick(event: any): void;
    findListItem(element: any): any;
    onItemClick(event: any, item: any): void;
    moveUp(event: any, listElement: any): void;
    moveTop(event: any, listElement: any): void;
    moveDown(event: any, listElement: any): void;
    moveBottom(event: any, listElement: any): void;
    getSelectedListElements(listElement: any): any[];
}
