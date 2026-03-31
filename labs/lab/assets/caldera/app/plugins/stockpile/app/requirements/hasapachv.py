from plugins.stockpile.app.requirements.base_requirement import BaseRequirement


class Requirement(BaseRequirement):

    async def enforce(self, link, operation):
        """
        Enforce the requirement by checking if the operation has retrieved a specific fact.
        :param link: The link being executed.
        :param operation: The current operation object.
        :return: True if the required fact exists, otherwise False.
        """
        import logging
        #logging.info("--- checking if the operation contains the required fact ---")

        relationships = await operation.all_relationships()
        #logging.info(f"retrieved {len(relationships)} relationships so far.")

        required_trait = "apache.version"
        required_value = "Apache httpd 2.4.49"
        
        all_facts = await operation.all_facts()
        #logging.info(f"Checking current fact pool with {len(all_facts)} facts...")

        for fact in all_facts:
            #logging.debug(f"fact pool: trait={fact.trait}, value={fact.value}")
            if fact.trait == required_trait and fact.value == required_value:
                #logging.info(f"fact found: {required_trait} = {required_value}")
                return True  # fact found in the existing pool

        for relationship in relationships:
            source = relationship.source  # source fact
            target = relationship.target  # target fact

            #logging.debug(f"relationship: source={source.trait}:{source.value}, target={target.trait}:{target.value}")

            if (source.trait == required_trait and source.value == required_value) or \
               (target.trait == required_trait and target.value == required_value):
                #logging.info(f"found the required fact: {required_trait} = {required_value}")
                return True  # Fact found

        #if no match is found
        #logging.info(f"required fact '{required_trait} = {required_value}' not found.")
        return False

