/**
 * Trigger do Pedido: delega a lógica ao PedidoTriggerHandler.
 */
trigger PedidoTrigger on Pedido__c (before insert, before update, after insert, after update) {
    // PedidoLegadoHandler.run();  -- comentário não conta como referência
    if (FeatureManagement.checkPermission('Bypass_Pedido_Trigger')) {
        return;
    }
    Trigger_Setting__mdt setting = Trigger_Setting__mdt.getInstance('PedidoTrigger');
    PedidoTriggerHandler handler = new PedidoTriggerHandler(Trigger.new, Trigger.oldMap);
    handler.run(Trigger.operationType);
    if (Trigger.isAfter) {
        Account conta = new Account();
        PedidoService.buscar(Trigger.newMap.keySet());
    }
}
