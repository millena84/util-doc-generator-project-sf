/**
 * Limpa pedidos cancelados (classe SIMULADA para testes).
 * @author fixture
 */
public with sharing class OrderCleanupBatch implements Database.Batchable<sObject>, Database.Stateful, Database.AllowsCallouts {
    // implements Queueable  <- comentário: não é evidência
    private static final String CHAVE = 'SENTINELA_APEX_SEGREDO_NAO_RENDERIZAR';
    private String falsoCodigo = 'System.enqueueJob(new Fantasma());';
    public Integer processados = 0;

    public Database.QueryLocator start(Database.BatchableContext bc) {
        return Database.getQueryLocator('SELECT Id, Status__c FROM Order__c WHERE Status__c = \'Cancelled\'');
    }

    public void execute(Database.BatchableContext bc, List<sObject> scope) {
        processados += scope.size();
    }

    public void finish(Database.BatchableContext bc) {
        Database.executeBatch(new InvoiceSyncBatch(), 50);
    }
}
