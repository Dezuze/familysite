from datetime import date
from families.models import FamilyMember, Relationship

class AnniversaryDetector:
    """
    Detects members who have birthdays, wedding anniversaries,
    or death anniversaries on a given target date.
    """

    @classmethod
    def get_events_for_date(cls, target_date=None):
        if target_date is None:
            target_date = date.today()

        m = target_date.month
        d = target_date.day

        events = []

        # 1. Birthdays (living members with matching month & day)
        birthdays = FamilyMember.objects.filter(
            date_of_birth__month=m,
            date_of_birth__day=d,
            is_deceased=False
        ).select_related('family')

        for member in birthdays:
            events.append({
                'event_type': 'birthday',
                'member': member,
                'spouse': None,
                'date': target_date,
                'title': f"🎂 Wishing a very Happy Birthday to {member.name}!",
                'description': f"Warmest birthday greetings to {member.name} ({member.branch or member.family.branch if member.family else ''}). May you be blessed with abundant joy, health, and peace!",
            })

        # 2. Wedding Anniversaries
        anniversaries = FamilyMember.objects.filter(
            wedding_anniversary__month=m,
            wedding_anniversary__day=d,
            is_deceased=False
        ).select_related('family')

        processed_couples = set()
        for member in anniversaries:
            if member.id in processed_couples:
                continue

            # Find spouse if recorded in Relationship table
            spouse = None
            spouse_rel = Relationship.objects.filter(
                from_member=member,
                relation_type__iexact='SPOUSE'
            ).select_related('to_member').first()

            if spouse_rel and spouse_rel.to_member:
                spouse = spouse_rel.to_member
                processed_couples.add(spouse.id)

            processed_couples.add(member.id)

            display_title = f"💍 Happy Wedding Anniversary to {member.name}"
            if spouse:
                display_title += f" & {spouse.name}"
            display_title += "!"

            events.append({
                'event_type': 'wedding_anniversary',
                'member': member,
                'spouse': spouse,
                'date': target_date,
                'title': display_title,
                'description': f"Heartiest congratulations to the couple on their wedding anniversary! Wishing them continued love, unity, and blessings.",
            })

        # 3. Death Anniversaries (Remembrance)
        death_anniversaries = FamilyMember.objects.filter(
            date_of_death__month=m,
            date_of_death__day=d
        ).select_related('family')

        for member in death_anniversaries:
            years_str = ""
            if member.date_of_birth and member.date_of_death:
                years_str = f" ({member.date_of_birth.year} – {member.date_of_death.year})"

            events.append({
                'event_type': 'death_anniversary',
                'member': member,
                'spouse': None,
                'date': target_date,
                'title': f"🕊️ Remembering {member.name}{years_str}",
                'description': f"On this anniversary of the passing of {member.name}, we remember their cherished life, love, and legacy in the Kollamparampil family with solemn prayers.",
            })

        return events
