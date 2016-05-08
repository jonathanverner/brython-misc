import { EventEmitter } from 'angular2/core';
import { ControlValueAccessor } from 'angular2/common';
export declare class ToggleButton implements ControlValueAccessor {
    onLabel: string;
    offLabel: string;
    onIcon: string;
    offIcon: string;
    disabled: boolean;
    style: string;
    styleClass: string;
    onChange: EventEmitter<any>;
    checked: boolean;
    onModelChange: Function;
    onModelTouched: Function;
    private hover;
    getIconClass(): string;
    toggle(event: any): void;
    writeValue(value: any): void;
    registerOnChange(fn: Function): void;
    registerOnTouched(fn: Function): void;
}
