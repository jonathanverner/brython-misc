import { Message } from '../api/message';
export declare class Messages {
    value: Message[];
    closable: boolean;
    hasMessages(): boolean;
    getSeverityClass(): string;
    clear(event: any): void;
}
