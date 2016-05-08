import { OnInit, TemplateRef, ViewContainerRef } from 'angular2/core';
export declare class TreeNodeTemplateLoader implements OnInit {
    private viewContainer;
    node: any;
    template: TemplateRef;
    constructor(viewContainer: ViewContainerRef);
    ngOnInit(): void;
}
