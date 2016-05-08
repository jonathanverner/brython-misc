import { ControlValueAccessor } from 'angular2/common';
import { Dropdown } from './dropdown';
export declare class DropdownValueAccessor implements ControlValueAccessor {
    private host;
    onChange: (_: any) => void;
    onTouched: () => void;
    constructor(host: Dropdown);
    writeValue(value: any): void;
    registerOnChange(fn: (_: any) => void): void;
    registerOnTouched(fn: () => void): void;
}
