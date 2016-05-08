import { ElementRef, AfterViewInit, OnDestroy, EventEmitter, SimpleChange } from 'angular2/core';
import { DomHandler } from '../dom/domhandler';
import { ControlValueAccessor } from 'angular2/common';
export declare class Editor implements AfterViewInit, OnDestroy, ControlValueAccessor {
    private el;
    private domHandler;
    onTextChange: EventEmitter<any>;
    toolbar: any;
    style: string;
    styleClass: string;
    value: string;
    onModelChange: Function;
    onModelTouched: Function;
    selfChange: boolean;
    quill: any;
    constructor(el: ElementRef, domHandler: DomHandler);
    ngAfterViewInit(): void;
    writeValue(value: any): void;
    registerOnChange(fn: Function): void;
    registerOnTouched(fn: Function): void;
    ngOnChanges(changes: {
        [key: string]: SimpleChange;
    }): void;
    ngOnDestroy(): void;
}
