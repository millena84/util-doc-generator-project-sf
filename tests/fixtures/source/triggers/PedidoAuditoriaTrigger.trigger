trigger PedidoAuditoriaTrigger on Pedido__c (before update, after delete) {
    System.debug('Trigger.size ' + Trigger.size);
}
