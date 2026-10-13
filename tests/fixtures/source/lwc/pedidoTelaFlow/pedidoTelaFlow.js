import { LightningElement, api } from 'lwc';
import { FlowAttributeChangeEvent, FlowNavigationNextEvent } from 'lightning/flowSupport';
import { subscribe } from 'lightning/empApi';

export default class PedidoTelaFlow extends LightningElement {
    @api valor;
    @api status;
    @api codigo;

    @api validate() {
        return { isValid: this.valor > 0, errorMessage: 'Valor inválido' };
    }

    connectedCallback() {
        subscribe('/event/Pedido_Evento__e', -1, () => {});
    }

    handleChange(event) {
        this.dispatchEvent(new FlowAttributeChangeEvent('status', event.target.value));
        this.dispatchEvent(new FlowNavigationNextEvent());
    }
}
