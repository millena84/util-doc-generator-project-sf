/** Handler da PedidoTrigger. */
public with sharing class PedidoTriggerHandler {
    private List<Pedido__c> novos;
    private Map<Id, Pedido__c> antigos;

    public PedidoTriggerHandler(List<Pedido__c> novos, Map<Id, Pedido__c> antigos) {
        this.novos = novos;
        this.antigos = antigos;
    }

    public void run(System.TriggerOperation operacao) {
        Automation_Settings__c cfg = Automation_Settings__c.getInstance();
        if (cfg != null && cfg.Bypass_Triggers__c) {
            return;
        }
        List<Pedido__c> atuais = [SELECT Id, Valor__c FROM Pedido__c WHERE Id IN :novos WITH USER_MODE];
        SObjectAccessDecision d = Security.stripInaccessible(AccessType.READABLE, atuais);
    }
}
