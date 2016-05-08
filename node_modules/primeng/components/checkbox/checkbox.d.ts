import { EventEmitter } from 'angular2/core';
import { ControlValueAccessor } from 'angular2/common';
export declare class Checkbox implements ControlValueAccessor {
    value: any;
    name: string;
    disabled: boolean;
    onChange: EventEmitter<any>;
    model: any;
    onModelChange: Function;
    onModelTouched: Function;
    hover: boolean;
    checked: boolean;
    onClick(): void;
    isChecked(): boolean;
    removeValue(value: any): void;
    addValue(value: any): void;
    findValueIndex(value: any): number;
    writeValue(model: any): void;
    registerOnChange(fn: Function): void;
    registerOnTouched(fn: Function): void;
}
