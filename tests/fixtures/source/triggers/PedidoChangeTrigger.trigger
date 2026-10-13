trigger PedidoChangeTrigger on Pedido__ChangeEvent (after insert) {
    System.debug(Trigger.new.size());
}
