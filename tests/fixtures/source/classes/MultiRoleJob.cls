global inherited sharing class MultiRoleJob implements database.batchable<SObject>, schedulable {
    global Database.QueryLocator start(Database.BatchableContext bc) {
        String q = montarConsulta();
        return Database.getQueryLocator(q);
    }
    global void execute(Database.BatchableContext bc, List<SObject> scope) {}
    global void finish(Database.BatchableContext bc) {}
    global void execute(SchedulableContext sc) {
        Database.executeBatch(this, 100);
    }
    private String montarConsulta() { return 'SELECT Id FROM Account'; }
}
