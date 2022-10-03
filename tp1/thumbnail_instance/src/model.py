import logging


class ThumbnailGrouper:
    def __init__(self, path):
        self.path = path
        self.video_unique = {}
        self.video_countries = {}

    def add_date(self, video_id, country, trending_date) -> bool:

        self.video_unique.setdefault(video_id, [])
        self.video_countries.setdefault(video_id, [])
        trending_dates = self.video_unique[video_id]
        trending_countries = self.video_countries[video_id]

        if (not country in trending_countries):
            trending_countries.append(country)

        if (not trending_date in trending_dates):
            trending_dates.append(trending_date)

        if (len(trending_countries) >= 11 and len(trending_dates) >= 21):
            return True

        return False

        # # If we have the validated ID we return
        # if (os.path.exists(validated_id)):
        #     return

        # f = open(id, "a+")
        # f.seek(0)
        # lines = f.readlines()

        # # If we have the date then its not unique
        # if trending_date in f.readlines():
        #     return

        # length = len(lines)

        # if (length + 1 == 21):
        #     f.close()
        #     os.rename(id, validated_id)
        #     logging.info(f'Tenemos 21 dias en video: {video_id}')
        #     return

        # f.write(f'{trending_date}\n')
        # f.close()

        # if (video.content['trending_date'] != None and video.content['view_count'] != None):
        #     date = datetime.strptime(
        #         video.content['trending_date'], '%Y-%m-%dT%H:%M:%SZ')

        #     views = int(video.content['view_count'])
        #     self.group_date(date, views)
