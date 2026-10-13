public with sharing class PedidoService {
    public class PedidoException extends Exception {}
    public static List<Order__c> buscar(Set<Id> ids) {
        return [SELECT Id FROM Order__c WHERE Id IN :ids];
    }
}
