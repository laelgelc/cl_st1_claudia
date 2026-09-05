# Input data issues report

## Inconsistencies in `1000_best_pop_songs_denoised.md`

Despite the input document was intended to provide information about 1000 songs, only 996 valid YouTube URLs (ones that contain the `https://www.youtube.com/watch?v=' pattern) could be found.

The reasons are explained below.

### Missing entries

> 516- Savage Garden, Truly, Madly, Deeply - 2009 - [Savage Garden - Truly Madly Deeply (Official Video)](https://www.youtube.com/watch?v=WQnAxOQxQIU&list=RDWQnAxOQxQIU&start_radio=1)
>
> 513- Bruno Mars, Locked out of Heaven - The official music video for Bruno Mars' "Locked Out Of Heaven" from the album 'Unorthodox Jukebox'. Directed by Cameron Duddy & Bruno Mars, Oct. 15, 2012 - [Bruno Mars - Locked Out Of Heaven (Official Music Video)](https://www.youtube.com/watch?v=e-fA-gBCkj0&list=RDe-fA-gBCkj0&start_radio=1)

**Songs 514 and 515 are completely missing** from the `1000_best_pop_songs_denoised.md` file. If you check the original list, it jumps straight from 516 down to 513! So there were only 998 songs in the document.

> Action: Provide the YouTube URL for the missing 514 and 515 songs.
> Response:
> | Alternatives provided                       | Selected |
> |---------------------------------------------|----------|
> | https://www.youtube.com/watch?v=Soa3gO7tL-c |          |
> |                                             |          |
> |                                             |          |

 


### Duplicate entries

> 372- The Notorious B.I.G., "Big Poppa" - "Juicy" is the lead single from the 1994 debut album Ready to Die by The Notorious B.I.G. The track's production is built around a sample of the 1983 song "Juicy Fruit" by Mtume. The single reached No. 27 on the Billboard Hot 100. The autobiographical lyrics of The Notorious B.I.G. describe his past struggles and subsequent success in the hip hop industry. Directed by: Sean "Puffy" Combs - [The Notorious B.I.G. - Juicy (Official Video) [4K]](https://www.youtube.com/watch?v=_JZom_gVfuw&list=RDEM_uQu2suzhQwyacPk3GQKJg&start_radio=1)
> 
> 961- The Notorious B.I.G., Juicy - "Juicy" is the lead single from the 1994 debut album Ready to Die by The Notorious B.I.G... Directed by: Sean "Puffy" Combs - [The Notorious B.I.G. - Juicy (Official Video) [4K]](https://www.youtube.com/watch?v=_JZom_gVfuw&list=RD_JZom_gVfuw&start_radio=1)

Songs 372 and 961 are duplicates.

> Action: Choose another song to replace the duplicate.

### Entry missing YouTube URL

> 971- Sly and the Family Stone, Thank you (Fallettinme Be Mice Elf again) - 1970 - Official Alternate Mix for "Thank You (Falettinme Be Mice Elf Agin)" by Sly & The Family Stone

Song 971's entry bears no YouTube URL.

> Action: Provide the YouTube URL for the song.

## Music video unavailable

The uploader (channel owner) of the following 11 songs made the music video unavailable for the region where the researcher is based, Brazil.

- https://www.youtube.com/watch?v=Tw6HrI9e1K4
- https://www.youtube.com/watch?v=YMDrTMnm1IE
- https://www.youtube.com/watch?v=a-C9pUGszsw
- https://www.youtube.com/watch?v=W_ykpby0yag
- https://www.youtube.com/watch?v=t6gcxNFc1I0
- https://www.youtube.com/watch?v=4fWyzwo1xg0
- https://www.youtube.com/watch?v=c3Hqy88oLIg
- https://www.youtube.com/watch?v=rZoD8JEFjAE
- https://www.youtube.com/watch?v=6WTdTwcmxyo
- https://www.youtube.com/watch?v=NOGEyBeoBGM
- https://www.youtube.com/watch?v=plcmqP3b-Qg

> Action: Use a VPN to connect from Brazil and click on the links to confirm that the music videos are unavailable. Choose replacement songs and confirm that they can be viewed from Brazil.

## Response format

The suggested actions account for 15 songs to complete the set of 1000 songs.

In your response, the only relevant piece of information is the YouTube "clean" URL for each song. Do not include any other text in your response because we are extracting the metadata directly from YouTube and including them in the [music videos dataset (XLSX)](https://github.com/laelgelc/cl_st1_claudia/blob/main/cl_st1_ph1_claudia/corpus/00_sources/music_videos_dataset.xlsx).

Example:

YouTube URL with accessory parameters `list` and `start_radio` for song 1000:

> https://www.youtube.com/watch?v=4xqo7D2k8HM&list=RD4xqo7D2k8HM&start_radio=1

The clean YouTube URL for song 1000 only contains the essential `v` parameter which identifies the video ID.

> https://www.youtube.com/watch?v=4xqo7D2k8HM
