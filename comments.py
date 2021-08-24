def get_comment_count(repos, start_date, end_date, state):
    results = {}
    for repo in repos:
        pulls = filter(lambda x: end_date >= x.created_at >= start_date, [i for i in repo.get_pulls(state=state)])
        comments_data = {}
        for pull in pulls:
            comments = [i for i in pull.get_comments()]
            for comment in comments:
                comments_data[comment.user.login] = comments_data.get(comment.user.login, 0) + 1

        for login, count in comments_data.items():
            _tmp = results.get(login, {})
            _tmp.update({repo.name: comments_data[login]})
            results[login] = _tmp
    return results


def comments_count_and_depth(repos, start_date, end_date, state):
    results = {}
    for repo in repos:
        pulls = filter(lambda x: end_date >= x.created_at >= start_date, [i for i in repo.get_pulls(state=state)])
        comments_data = {}
        for pull in pulls:
            comments = [i for i in pull.get_comments()]
            counted = set()
            for comment in comments:
                _tmp = comments_data.get(comment.user.login, {'comments_count': 0, 'depth': 0.0, 'pr_count': 0})
                _tmp['comments_count'] += 1
                if comment.user.login not in counted:
                    _tmp['pr_count'] += 1
                counted.add(comment.user.login)
                comments_data[comment.user.login] = _tmp

        for login, data in comments_data.items():
            data['depth'] = data['comments_count'] / data['pr_count']
            _tmp = results.get(login, {})
            _tmp.update({repo.name: data})
            results[login] = _tmp
    return results
