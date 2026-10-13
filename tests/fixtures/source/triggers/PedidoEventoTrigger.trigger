trigger PedidoEventoTrigger on Pedido_Evento__e (after insert) {
    PedidoService.buscar(new Set<Id>());
}
