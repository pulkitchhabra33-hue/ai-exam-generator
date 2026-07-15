def merge_metadata(blueprint, metadata):
    metadata_map= {}

    for item in metadata['questions']:
        metadata_map[item['question_no']] = item

    for question in blueprint['questions']:
        item= metadata_map.get(
            question['question_no']
        )

        if item:
            question['subject']= item['subject']
            question["chapter"] = item["chapter"]
            question["concept"] = item["concept"]
            question["difficulty"] = item["difficulty"]
            question["cognitive"] = item["cognitive"]

    return blueprint
