"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var core_1 = require('angular2/core');
var common_1 = require('angular2/common');
var lang_1 = require('angular2/src/facade/lang');
var di_1 = require('angular2/src/core/di');
var dropdown_1 = require('./dropdown');
var CUSTOM_VALUE_ACCESSOR = lang_1.CONST_EXPR(new core_1.Provider(common_1.NG_VALUE_ACCESSOR, { useExisting: di_1.forwardRef(function () { return DropdownValueAccessor; }), multi: true }));
var DropdownValueAccessor = (function () {
    function DropdownValueAccessor(host) {
        this.host = host;
        this.onChange = function (_) { };
        this.onTouched = function () { };
    }
    DropdownValueAccessor.prototype.writeValue = function (value) {
        this.host.value = value;
        console.log('Value:' + value);
        if (this.host.initialized) {
            console.log('ui up');
            this.host.updateUI();
        }
    };
    DropdownValueAccessor.prototype.registerOnChange = function (fn) { this.onChange = fn; };
    DropdownValueAccessor.prototype.registerOnTouched = function (fn) { this.onTouched = fn; };
    DropdownValueAccessor = __decorate([
        core_1.Directive({
            selector: 'p-dropdown',
            host: { '(onChange)': 'onChange($event)' },
            providers: [CUSTOM_VALUE_ACCESSOR]
        }), 
        __metadata('design:paramtypes', [dropdown_1.Dropdown])
    ], DropdownValueAccessor);
    return DropdownValueAccessor;
}());
exports.DropdownValueAccessor = DropdownValueAccessor;
//# sourceMappingURL=dropdownvalueaccessor.js.map