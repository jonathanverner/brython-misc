export interface MenuItem {
    icon?: string;
    label?: string;
    click?: any;
    url?: any;
}
export interface SubMenu {
    icon?: string;
    label?: string;
    items?: MenuItem[];
}
