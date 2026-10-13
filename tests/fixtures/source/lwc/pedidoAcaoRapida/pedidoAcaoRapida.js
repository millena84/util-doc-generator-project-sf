import { LightningElement, api } from 'lwc';
import enviar from '@salesforce/apex/PedidoController.enviar';

export default class PedidoAcaoRapida extends LightningElement {
    @api recordId;

    @api invoke() {
        return enviar({ pedidoId: this.recordId });
    }
}
