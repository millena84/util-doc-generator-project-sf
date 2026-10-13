import { LightningElement, api } from 'lwc';
import { FlowAttributeChangeEvent, FlowNavigationNextEvent } from 'lightning/flowSupport';

export default class PedidoTelaFlow extends LightningElement {
    @api valor;
    @api status;
    @api codigo;

    @api validate() {
        return { isValid: this.valor > 0, errorMessage: 'Valor inválido' };
    }

    handleChange(event) {
        this.dispatchEvent(new FlowAttributeChangeEvent('status', event.target.value));
        this.dispatchEvent(new FlowNavigationNextEvent());
    }
}
