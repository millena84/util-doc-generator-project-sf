import { LightningElement, api, wire } from 'lwc';
import { getRecord } from 'lightning/uiRecordApi';
import { publish, MessageContext } from 'lightning/messageService';
import buscarPedidos from '@salesforce/apex/PedidoController.buscarPedidos';
import contarPedidos from '@salesforce/apex/PedidoController.contarPedidos';
import enviar from '@salesforce/apex/PedidoController.enviar';
import PODE_APROVAR from '@salesforce/customPermission/Aprova_Pedido';
import PEDIDO_SELECIONADO from '@salesforce/messageChannel/Pedido_Selecionado__c';
import VALOR_FIELD from '@salesforce/schema/Pedido__c.Valor__c';
// import legado from '@salesforce/apex/LegadoController.metodo';

/* Painel de pedidos (simulado). */
export default class PedidoPainel extends LightningElement {
    @api recordId;
    @api objectApiName;
    @api titulo = 'Pedidos';

    @wire(MessageContext) messageContext;
    @wire(getRecord, { recordId: '$recordId', fields: [VALOR_FIELD] }) pedido;
    @wire(buscarPedidos, { recordId: '$recordId' }) pedidos;
    @wire(contarPedidos) total;

    get podeAprovar() {
        return PODE_APROVAR;
    }

    connectedCallback() {
        this.texto = "new CustomEvent('falso')";
    }

    disconnectedCallback() {}

    handleEnviar() {
        enviar({ pedidoId: this.recordId }).then(() => {
            publish(this.messageContext, PEDIDO_SELECIONADO, { recordId: this.recordId });
            this.dispatchEvent(new CustomEvent('pedidoselecionado', { detail: this.recordId }));
        });
    }
}
