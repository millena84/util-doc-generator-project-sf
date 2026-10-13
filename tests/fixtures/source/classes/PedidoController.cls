/** Controller Apex dos LWCs de pedido (simulado). */
public with sharing class PedidoController {
    @AuraEnabled(cacheable=true)
    public static List<Pedido__c> buscarPedidos(Id recordId) {
        return [SELECT Id, Valor__c FROM Pedido__c WHERE Id = :recordId WITH USER_MODE];
    }

    @AuraEnabled
    public static Integer contarPedidos() {
        return [SELECT COUNT() FROM Pedido__c];
    }

    @AuraEnabled
    public static void enviar(Id pedidoId) {
        Pedido_Evento__e evento = new Pedido_Evento__e(Numero_Pedido__c = String.valueOf(pedidoId));
        EventBus.publish(evento);
    }
}
