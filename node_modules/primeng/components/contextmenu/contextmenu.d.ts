import { ElementRef, SimpleChange } from 'angular2/core';
export declare class ContextMenu {
    private el;
    global: boolean;
    style: string;
    styleClass: string;
    initialized: boolean;
    menuElement: any;
    constructor(el: ElementRef);
    ngAfterViewInit(): void;
    ngOnChanges(changes: {
        [key: string]: SimpleChange;
    }): void;
    ngOnDestroy(): void;
    show(event: any): void;
}
